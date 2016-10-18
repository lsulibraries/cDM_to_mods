#! /usr/bin/env python3

import os
import sys
import logging
from shutil import copyfile
import json
from lxml import etree as ET

source_dir = "U:/Cached_Cdm_files/" # Windows source
# source_dir = '/media/francis/U/Cached_Cdm_files/' # garrett's laptop
# source_dir = add yours here.

# usage is:
#    path/to/the/directory/cDM_to_mods/python3 post_conversion_cleanup.py $alias_name
#    i.e.  python3 post_conversion_cleanup.py p16313coll16


class IsCountsCorrect():
    def __init__(self, alias):
        list_of_etrees = IsCountsCorrect.make_etrees_of_Elems_In(alias)
        root_count = IsCountsCorrect.get_root_count_from_etrees(list_of_etrees)
        root_compounds = IsCountsCorrect.name_root_compounds(list_of_etrees)
        simples = root_count - len(root_compounds)
        compounds = 0
        for parent in root_compounds:
            compounds += IsCountsCorrect.count_child_pointers(alias, parent)
            compounds += 1  # we count compound root objects as 1 item here.

        logging.info('Count Simples xmls: {}'.format(simples))
        logging.info('Count Compounds xmls: {}'.format(compounds))
        if simples == IsCountsCorrect.count_observed_simples(alias):
            logging.info('simples metadata counts match')
        else:
            logging.warning("BIG DEAL:  Simples Don't Match")
        if compounds == IsCountsCorrect.count_observed_compounds(alias):
            logging.info('compounds metadata counts match')
        else:
            logging.warning("BIG DEAL:  Compounds Don't Match")
        logging.info('IsCountsCorrect done')

    @staticmethod
    def make_etrees_of_Elems_In(alias):
        input_dir = os.path.abspath(os.path.join(source_dir, alias))
        elems_files = ["{}/{}".format(input_dir, i) for i in os.listdir(input_dir)
                       if 'Elems_in_Collection' in i and '.xml' in i]
        return [ET.parse(i) for i in elems_files]

    @staticmethod
    def get_root_count_from_etrees(list_of_etrees):
        set_total_at_root_level = {int(elems_etree.find('./pager/total').text) for elems_etree in list_of_etrees}
        if len(set_total_at_root_level) == 1:
            return set_total_at_root_level.pop()
        else:
            logging.warning('BIG DEAL:  either Elems_in_Collection has mismatched number of total counts, or an Elems_in is unreadable')
            return False

    @staticmethod
    def name_root_compounds(list_of_etrees):
        compound_pointers = []
        for i in list_of_etrees:
            for elem in i.findall('.//record/filetype'):
                if elem.text == 'cpd':
                    pointers = {p.text for p in elem.itersiblings(preceding=True) if p.tag == 'pointer'}.union(
                               {p.text for p in elem.itersiblings() if p.tag == 'pointer'})
                    dmrecords = {p.text for p in elem.itersiblings(preceding=True) if p.tag == 'dmrecord'}.union(
                                {p.text for p in elem.itersiblings() if p.tag == 'dmrecord'})
                    if pointers:
                        compound_pointers.append(pointers.pop())
                    elif dmrecords:
                        compound_pointers.append(dmrecords.pop())
        return compound_pointers

    @staticmethod
    def count_child_pointers(alias, cpd_pointer):
        structure_file = os.path.abspath(os.path.join(source_dir, alias, 'Cpd/{}_cpd.xml'.format(cpd_pointer)))
        structure_etree = ET.parse(structure_file)
        child_pointers = [i.text for i in structure_etree.findall('./page/pageptr')]
        return len(child_pointers)

    @staticmethod
    def count_observed_simples(alias):
        for root, dirs, files in os.walk(os.path.abspath('output')):
            if root.split('/')[-1] == '{}_simples'.format(alias):
                output_dir = '{}/final_format/'.format(root)
                for root, dirs, files in os.walk(output_dir):
                    return len([i for i in files if ".xml" in i])

    @staticmethod
    def count_observed_compounds(alias):
        for root, dirs, files in os.walk(os.path.abspath('output')):
            if root.split('/')[-1] == '{}_compounds'.format(alias):
                output_dir = '{}/final_format/'.format(root)
                compounds_count = 0
                for root, dirs, files in os.walk(output_dir):
                    compounds_count += len([i for i in files if i == "MODS.xml"])
                return compounds_count


class PullInBinaries():
    def __init__(self, alias):
        sourcefiles_paths = PullInBinaries.makedict_sourcefiles(alias)
        simplexmls_list = PullInBinaries.makelist_simpleoutfolderxmls(alias)
        compoundxmls_list = PullInBinaries.makelist_compoundoutfolderxmls(alias)
        for filelist in (simplexmls_list, compoundxmls_list):
            for kind, outroot, pointer in filelist:
                if pointer not in sourcefiles_paths:
                    if kind == "compound" and outroot.split('/')[-2] == "final_format":
                        continue  # root of cpd is expected to have no binary
                    else:
                        logging.warning("{} pointer {} has no matching binary".format(kind, pointer))
                if PullInBinaries.is_binary_in_output_dir(kind, outroot, pointer):
                    continue
                if pointer not in sourcefiles_paths:
                    continue
                sourcepath, sourcefile = sourcefiles_paths[pointer]
                PullInBinaries.copy_binary(kind, sourcepath, sourcefile, outroot, pointer)
        logging.info('PullInBinaries done')

    @staticmethod
    def makedict_sourcefiles(alias):
        sourcefiles_paths = dict()
        input_dir = os.path.join(source_dir, alias)
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.split('.')[-1] in ('jp2', 'mp4', 'mp3', 'pdf'):
                    alias = file.split('.')[0]
                    sourcefiles_paths[alias] = (root, file)
        return sourcefiles_paths

    @staticmethod
    def makelist_simpleoutfolderxmls(alias):
        xml_filelist = []
        subfolder = os.path.abspath(os.path.join('output', '{}_simples'.format(alias), 'final_format'))
        for root, dirs, files in os.walk(subfolder):
            for file in files:
                if '.xml' in file:
                    pointer = file.split('.')[0]
                    xml_filelist.append(('simple', root, pointer))
        return xml_filelist

    @staticmethod
    def makelist_compoundoutfolderxmls(alias):
        xml_filelist = []
        subfolder = os.path.abspath(os.path.join('output', '{}_compounds'.format(alias), 'final_format'))
        for root, dirs, files in os.walk(subfolder):
            for file in files:
                if file == 'MODS.xml':
                    pointer = root.split('/')[-1]
                    xml_filelist.append(('compound', root, pointer))
        return xml_filelist

    @staticmethod
    def is_binary_in_output_dir(kind, root, pointer):
        acceptable_binary_types = ('mp3', 'mp4', 'jp2', 'pdf')
        if kind == 'simple':
            for filetype in acceptable_binary_types:
                if os.path.isfile(os.path.join(root, '{}.{}'.format(pointer, filetype))):
                    return True
        if kind == 'compound':
            for filetype in acceptable_binary_types:
                if os.path.isfile(os.path.join(root, pointer, 'OBJ.{}'.format(filetype))):
                    return True
        return False

    @staticmethod
    def copy_binary(kind, sourcepath, sourcefile, outroot, pointer):
        if kind == 'simple':
            copyfile(os.path.join(sourcepath, sourcefile), os.path.join(outroot, sourcefile))
        elif kind == 'compound':
            copyfile(os.path.join(sourcepath, sourcefile), os.path.join(outroot, "OBJ.{}".format(sourcefile.split('.')[-1])))


class MakeStructureFile():
    def __init__(self, alias):
        for root, dirs, files in os.walk('output'):
            if 'structure.cpd' in files:
                parent = root.split("/")[-1]
                new_etree = ET.Element("islandora_compound_object", title=parent)
                old_etree = ET.parse("{}/structure.cpd".format(root))
                for i in old_etree.findall('.//pageptr'):
                    new_etree.append(ET.Element('child', content=i.text))

                with open('{}/structure.xml'.format(root), 'wb') as f:
                    f.write(ET.tostring(new_etree, encoding="utf-8", xml_declaration=True, pretty_print=True))
        logging.info('MakeStructureFile done')


def report_restricted_files(alias):
    restrictions_dict = dict()
    all_metadatas = []
    simples_metadatas = ["{}/{}".format(root, file)
                         for root, dirs, files in os.walk('output/{}_simples/final_format'.format(alias))
                         for file in files
                         if '.xml' in file]
    all_metadatas.extend(simples_metadatas)
    compounds_metadatas = ["{}/{}".format(root, file)
                           for root, dirs, files in os.walk('output/{}_compounds/final_format'.format(alias))
                           for file in files
                           if '.xml' in file]
    all_metadatas.extend(compounds_metadatas)
    for mods in all_metadatas:
        pointer = mods.split('/')[-1]
        mods_etree = ET.parse(mods).getroot()
        for child in mods_etree.iterfind('.//{http://www.loc.gov/mods/v3}dmGetItemInfo'):
            original_metadata = json.loads(child.text)
            restriction = original_metadata['dmaccess']
            if restriction:
                logging.warning('{} must be restricted to {}'.format(alias, restriction))
                restrictions_dict[pointer] = restriction
    if restrictions_dict:
        output_text = ''
        with open('output/{}_restrictions.txt'.format(alias), 'w') as f:
            for k, v in restrictions_dict.items():
                output_text += '{}: {}\n'.format(k.replace('.xml', ''), v)
            f.write(output_text)
        logging.info('report_restricted_files done')
        logging.info('List of restricted items in file at output/{}_restricted_item.txt'.format(alias))
    else:
        logging.info('report_restricted_files done.')
        logging.info('No restricted items.')


def setup_logging():
    logging.basicConfig(filename='post_conversion_cleanup_log.txt',
                        level=logging.INFO,
                        format='%(asctime)s: %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def name_outputted_collections():
    return set(root.split('/')[-1].replace('_compounds', '').replace('_simples', '') for root, dirs, files in os.walk('output') if 'final_format' in dirs)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        alias = sys.argv[1]
        setup_logging()
        logging.info('starting {}'.format(alias))
        PullInBinaries(alias)
        MakeStructureFile(alias)
        IsCountsCorrect(alias)
        report_restricted_files(alias)
        llogging.info('finished {}'.format(alias))
    else:
        for alias in name_outputted_collections():
            print(alias)
            setup_logging()
            logging.info('starting {}'.format(alias))
            PullInBinaries(alias)
            MakeStructureFile(alias)
            IsCountsCorrect(alias)
            report_restricted_files(alias)
            logging.info('finished {}'.format(alias))
