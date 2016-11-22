#! /usr/bin/env python3

import os
import sys
import logging
from shutil import copyfile, move
import json
from lxml import etree as ET


class IsCountsCorrect():
    def __init__(self, alias, cdm_data_dir):
        list_of_json_elems_files = self.make_list_of_elem_jsons(alias, cdm_data_dir)
        root_count_json = self.get_root_count(list_of_json_elems_files)
        root_compounds_json = self.name_root_compounds_json(list_of_json_elems_files)

        simples = root_count_json - len(root_compounds_json)
        compounds = 0
        for parent in root_compounds_json:
            compounds += self.count_child_pointers(alias, parent, cdm_data_dir)
            compounds += 1  # we count compound root objects as 1 item here.

        logging.info('Count Simples xmls: {}'.format(simples))
        logging.info('Count Compounds xmls: {}'.format(compounds))
        if simples == self.count_observed_simples(alias):
            logging.info('simples metadata counts match')
        else:
            logging.warning("BIG DEAL:  Simples Don't Match.  Expected: {}.  Observed: {}".format(simples, self.count_observed_simples(alias)))
        if compounds == self.count_observed_compounds(alias):
            logging.info('compounds metadata counts match')
        else:
            logging.warning("BIG DEAL:  Compounds Don't Match.  Expected: {}.  Observed: {}".format(compounds, self.count_observed_compounds(alias)))
        logging.info('IsCountsCorrect done')

    def make_list_of_elem_jsons(self, alias, cdm_data_dir):
        input_dir = os.path.join(cdm_data_dir, alias)
        return [os.path.join(input_dir, file) for file in os.listdir(input_dir)
                if 'Elems_in_Collection' in file and '.json' in file]

    def get_root_count(self, list_of_json_files):
        named_total = set()
        for file in list_of_json_files:
            with open(file, 'r', encoding='utf-8') as f:
                parsed_json = json.loads(f.read())
            named_total.add(parsed_json['pager']['total'])
        if len(named_total) == 1:
            return named_total.pop()
        else:
            logging.warning('BIG DEAL:  either Elems_in_Collection has mismatched number of total counts, or an Elems_in is unreadable')
            return False

    def name_root_compounds_json(self, list_of_json_files):
        compound_pointers = []
        for file in list_of_json_files:
            with open(file, 'r', encoding='utf-8') as f:
                parsed_json = json.loads(f.read())
            for item in parsed_json['records']:
                if item["filetype"] == "cpd":
                    pointer = item['pointer'] or item['dmrecord']
                    compound_pointers.append(str(pointer))
        return compound_pointers

    def count_child_pointers(self, alias, cpd_pointer, cdm_data_dir):
        structure_file = os.path.abspath(os.path.join(cdm_data_dir, alias, 'Cpd/{}_cpd.xml'.format(cpd_pointer)))
        structure_etree = ET.parse(structure_file)
        child_pointers = [i for i in structure_etree.findall('//pageptr') if i.text]
        return len(child_pointers)

    def count_observed_simples(self, alias):
        output_dir = os.path.join('output', '{}_simples'.format(alias), 'final_format')
        if not os.path.isdir(output_dir):
            return 0
        simple_files = [i for i in os.listdir(output_dir) if ".xml" in i]
        return len(simple_files)

    def count_observed_compounds(self, alias):
        output_dir = os.path.join('output', '{}_compounds'.format(alias), 'final_format')
        compounds_files = []
        for root, dirs, files in os.walk(output_dir):
            compounds_files.extend([i for i in files if i == "MODS.xml"])
        return len(compounds_files)


class PullInBinaries():
    def __init__(self, alias, cdm_data_dir):
        sourcefiles_paths = self.makedict_sourcefiles(alias, cdm_data_dir)
        simplexmls_list = self.makelist_simpleoutfolderxmls(alias)
        compoundxmls_list = self.makelist_compoundoutfolderxmls(alias)
        for filelist in (simplexmls_list, compoundxmls_list):
            for kind, outroot, pointer in filelist:
                if pointer not in sourcefiles_paths:
                    if kind == "compound" and os.path.split(os.path.split(outroot)[0])[1] == "final_format":
                        continue  # root of cpd is expected to have no binary
                    else:
                        logging.warning("{} pointer {} has no matching binary".format(kind, pointer))
                if self.is_binary_in_output_dir(kind, outroot, pointer):
                    continue
                if pointer not in sourcefiles_paths:
                    continue
                sourcepath, sourcefile = sourcefiles_paths[pointer]
                self.copy_binary(kind, sourcepath, sourcefile, outroot, pointer)
        logging.info('PullInBinaries done')

    def makedict_sourcefiles(self, alias, cdm_data_dir):
        sourcefiles_paths = dict()
        input_dir = os.path.join(cdm_data_dir, alias)
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.split('.')[-1] in ('jp2', 'mp4', 'mp3', 'pdf'):
                    pointer = file.split('.')[0]
                    if pointer in sourcefiles_paths:
                        logging.warning("pointer {} has multiple possible source binaries -- please cull unwanted version".format(pointer))
                        quit()
                    sourcefiles_paths[pointer] = (root, file)
        return sourcefiles_paths

    def makelist_simpleoutfolderxmls(self, alias):
        xml_filelist = []
        subfolder = os.path.abspath(os.path.join('output', '{}_simples'.format(alias), 'final_format'))
        for root, dirs, files in os.walk(subfolder):
            for file in files:
                if '.xml' in file:
                    pointer = file.split('.')[0]
                    xml_filelist.append(('simple', root, pointer))
        return xml_filelist

    def makelist_compoundoutfolderxmls(self, alias):
        xml_filelist = []
        subfolder = os.path.abspath(os.path.join('output', '{}_compounds'.format(alias), 'final_format'))
        for root, dirs, files in os.walk(subfolder):
            for file in files:
                if file == 'MODS.xml':
                    pointer = os.path.split(root)[-1]
                    xml_filelist.append(('compound', root, pointer))
        return xml_filelist

    def is_binary_in_output_dir(self, kind, root, pointer):
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

    def copy_binary(self, kind, sourcepath, sourcefile, outroot, pointer):
        if kind == 'simple':
            copyfile(os.path.join(sourcepath, sourcefile), os.path.join(outroot, sourcefile))
        elif kind == 'compound':
            copyfile(os.path.join(sourcepath, sourcefile), os.path.join(outroot, "OBJ.{}".format(sourcefile.split('.')[-1])))


class MakeStructureFile():
    def __init__(self, alias):
        for root, dirs, files in os.walk('output'):
            if 'structure.cpd' in files:
                parent = os.path.split(root)[-1]
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
        pointer = os.path.split(mods)[-1]
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


def report_filetype(alias):
    filetypes = set()
    all_binaries = []
    simples_binaries = ["{}/{}".format(root, file)
                        for root, dirs, files in os.walk('output/{}_simples/final_format'.format(alias))
                        for file in files
                        if '.xml' not in file]
    all_binaries.extend(simples_binaries)
    compounds_binaries = ["{}/{}".format(root, file)
                          for root, dirs, files in os.walk('output/{}_compounds/final_format'.format(alias))
                          for file in files
                          if '.xml' not in file]
    all_binaries.extend(compounds_binaries)
    for binary_filename in all_binaries:
        filetypes.add(binary_filename.split('.')[-1])
    logging.info('Collection contains filetypes: {}'.format(filetypes))


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


def folder_by_extension(alias):
    starting_folder = os.path.join('output', '{}_simples'.format(alias), 'final_format')
    if not os.path.isdir(starting_folder):
        return
    files = [i for i in os.listdir(starting_folder) if os.path.isfile(os.path.join(starting_folder, i))]
    extensions = {i.split(".")[1] for i in files if i.split(".")[1] != 'xml'}
    for extension in extensions:
        os.makedirs(os.path.join(starting_folder, extension), exist_ok=True)
        files_limited_to_extension = {file.split('.')[0] for file in files if file.split('.')[1] == extension}
        files_with_extension_plus_samenames = [file for file in files if file.split('.')[0] in files_limited_to_extension]
        for file in files_with_extension_plus_samenames:
            move(os.path.join(starting_folder, file), os.path.join(starting_folder, extension, file))


if __name__ == '__main__':
    setup_logging()
    try:
        alias = sys.argv[1]
        cdm_data_dir = sys.argv[2]
    except IndexError:
        logging.warning('')
        logging.warning('Change to: "python post_conversion_cleanup.py $aliasname $path/to/U-Drive/Cached_Cdm_files"')
        logging.warning('')
        quit()
    logging.info('starting {}'.format(alias))
    PullInBinaries(alias, cdm_data_dir)
    MakeStructureFile(alias)
    IsCountsCorrect(alias, cdm_data_dir)
    report_restricted_files(alias)
    report_filetype(alias)
    folder_by_extension(alias)
    logging.info('finished {}'.format(alias))
