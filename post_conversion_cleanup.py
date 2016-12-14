#! /usr/bin/env python3

import os
import sys
import shutil
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
            quit()
        if compounds == self.count_observed_compounds(alias):
            logging.info('compounds metadata counts match')
        else:
            logging.warning("BIG DEAL:  Compounds Don't Match.  Expected: {}.  Observed: {}".format(compounds, self.count_observed_compounds(alias)))
            quit()
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
                        quit()
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
                restrictions_dict[pointer] = restriction
    if restrictions_dict:
        output_text = ''
        with open('output/{}_restrictions.txt'.format(alias), 'w') as f:
            for k, v in restrictions_dict.items():
                output_text += '{}: {}\n'.format(k.replace('.xml', ''), v)
            f.write(output_text)
        logging.info('report_restricted_files done')
        logging.warning('Add a "Restricted" Label to the {} ETL card'.format(alias))
        logging.warning('Add output/{}_restrictions.txt to the card'.format(alias))
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


def make_zips(alias):
    os.makedirs('Upload_to_Islandora', exist_ok=True)
    institution = lookup_institution(alias)

    cpd_output = 'output/{}_compounds/final_format'.format(alias)
    if os.path.isdir(cpd_output):
        zipfilename = 'Upload_to_Islandora/{}-{}-cpd'.format(institution, alias)
        shutil.make_archive(zipfilename, 'zip', cpd_output)
        logging.info('{}.zip created'.format(zipfilename))

    simple_output = 'output/{}_simples/final_format'.format(alias)
    if os.path.isdir(simple_output):
        subdirs = [i for i in os.listdir(simple_output) if os.path.isdir(os.path.join(simple_output, i))]
        for subdir in subdirs:
            subdir_path = os.path.join(simple_output, subdir)
            zipfilename = 'Upload_to_Islandora/{}-{}-{}'.format(institution, alias, subdir)
            shutil.make_archive(zipfilename, 'zip', subdir_path)
            logging.info('{}.zip created'.format(zipfilename))


def lookup_institution(alias):
    inst_colls = {'lsuhscs': ['lsuhscs_gwm', 'p15140coll23', 'p15140coll44', 'p16313coll3'],
                  'state': ['lhp', 'lwp', 'p267101coll4'],
                  'tulane': ['ama', 'htu', 'p15140coll15', 'p15140coll24', 'p15140coll25', 'p15140coll29', 'p15140coll3', 'p15140coll34', 'p15140coll37', 'p15140coll38', 'p15140coll39', 'p15140coll40', 'p15140coll45', 'p15140coll47', 'p15140coll58', 'p15140coll9', 'p16313coll11', 'p16313coll12', 'p16313coll13', 'p16313coll14', 'p16313coll15', 'p16313coll16', 'p16313coll27', 'p16313coll29', 'p16313coll30', 'p16313coll33', 'p16313coll37', 'p16313coll38', 'p16313coll39', 'p16313coll4', 'p16313coll40', 'p16313coll41', 'p16313coll42', 'p16313coll46', 'p16313coll47', 'p16313coll53', 'p16313coll59', 'p16313coll6', 'p16313coll63', 'p16313coll64', 'p16313coll66', 'p16313coll68', 'p16313coll71', 'p16313coll73', 'p16313coll75', 'p16313coll78', 'p16313coll84'],
                  'lsuhsc': ['lsubk01', 'lsuhsc_ncc', 'p120701coll26', 'p120701coll7', 'p15140coll16', 'p15140coll19', 'p15140coll49', 'p15140coll50', 'p15140coll52', 'p16313coll19'],
                  'hnoc': ['aww', 'clf', 'lph', 'p15140coll1', 'p15140coll28', 'p15140coll33', 'p15140coll43', 'p15140coll61', 'p16313coll17', 'p16313coll21', 'p16313coll36', 'p16313coll65'],
                  'lsm': ['cca', 'fjc', 'gfm', 'hlm', 'jaz', 'jnt', 'lct', 'lhc', 'loh', 'lps', 'lsm_ccc', 'lsm_fqa', 'lsm_koh', 'lsm_mpc', 'lsm_nac', 'lsm_ncc', 'lst', 'osc', 'p120701coll18', 'p15140coll22', 'p15140coll60', 'p16313coll83', 'rmc', 'rsp', 'rtc'],
                  'uno': ['fbm', 'hic', 'omsa', 'p120701coll13', 'p120701coll15', 'p120701coll25', 'p120701coll29', 'p120701coll8', 'p15140coll30', 'p15140coll31', 'p15140coll4', 'p15140coll42', 'p15140coll53', 'p15140coll7', 'p16313coll18', 'p16313coll2', 'p16313coll22', 'p16313coll23', 'p16313coll60', 'p16313coll61', 'p16313coll62', 'p16313coll7', 'p16313coll72', 'p16313coll86', 'uno_ani', 'uno_jbf'],
                  'nsu': ['mpa', 'ncc'],
                  'ulm': ['p120701coll10', 'p15140coll26', 'p15140coll27', 'p16313coll1', 'p16313coll43'],
                  'mcneese': ['p16313coll74', 'psl'],
                  'tahil': ['aaw', 'abw', 'apc', 'bba', 'hpl', 'lpc', 'rtp', 'tah'],
                  'ull': ['acc', 'lsa', 'p16313coll25', 'p16313coll26', 'sip'],
                  'latech': ['cmprt'],
                  'ldl': ['p16313coll97'],
                  'loyno': ['jsn', 'lmnp01', 'loyola_etd', 'loyola_etda', 'loyola_etdb', 'p120701coll17', 'p120701coll27', 'p120701coll28', 'p120701coll9', 'p16313coll20', 'p16313coll24', 'p16313coll28', 'p16313coll48', 'p16313coll5', 'p16313coll87', 'p16313coll91', 'p16313coll93', 'p16313coll95', 'p16313coll96', 'p16313coll98'],
                  'subr': ['hwj', 'vbc'],
                  'nicholls': ['p15140coll51'],
                  'lsus': ['lsus_tbp', 'nwm', 'stc'],
                  'lsu': ['brs', 'crd', 'cwd', 'hnf', 'ibe', 'lapur', 'lmp', 'lsap', 'lsu_act', 'lsu_brt', 'lsu_cff', 'lsu_clt', 'lsu_cnp', 'lsu_cwp', 'lsu_dyp', 'lsu_fcc', 'lsu_gcs', 'lsu_gfm', 'lsu_gsc', 'lsu_hpl', 'lsu_jja', 'lsu_lhc', 'lsu_lnp', 'lsu_mdp', 'lsu_mrf', 'lsu_nmi', 'lsu_noe', 'lsu_pvc', 'lsu_rbc', 'lsu_rbo', 'lsu_sce', 'lsu_tjp', 'lsu_uap', 'lsu_wls', 'mmf', 'msw', 'neworleans', 'nonegexposures', 'p120701coll12', 'p120701coll19', 'p120701coll22', 'p120701coll23', 'p120701coll24', 'p15140coll10', 'p15140coll12', 'p15140coll14', 'p15140coll17', 'p15140coll18', 'p15140coll21', 'p15140coll35', 'p15140coll41', 'p15140coll46', 'p15140coll54', 'p15140coll56', 'p15140coll6', 'p16313coll10', 'p16313coll31', 'p16313coll34', 'p16313coll35', 'p16313coll45', 'p16313coll51', 'p16313coll52', 'p16313coll54', 'p16313coll56', 'p16313coll57', 'p16313coll58', 'p16313coll69', 'p16313coll76', 'p16313coll77', 'p16313coll79', 'p16313coll8', 'p16313coll80', 'p16313coll81', 'p16313coll85', 'p16313coll89', 'p16313coll9', 'p16313coll92', 'rjr', 'sartainengravings', 'tensas', 'thw', 'tld', 'wri-boy'],
                  }
    for inst, colls in inst_colls.items():
        if alias.lower() in colls:
            return inst
    logging.warning('Couldnt find alias {} in lookup_institution'.format(alias))
    quit()


def move_zips_to_U(cdm_data_dir, alias):
    files = [os.path.join('Upload_to_Islandora', i) for i in os.listdir('Upload_to_Islandora') if alias.lower() in i]
    dest_drive = os.path.split(os.path.split(cdm_data_dir)[0])[0]
    dest_path = os.path.join(dest_drive, 'Upload_to_Islandora')
    os.makedirs(dest_path, exist_ok=True)
    for file in files:
        dest_file = os.path.split(file)[1]
        dest_filepath = os.path.join(dest_path, dest_file)
        shutil.move(file, dest_filepath)
        logging.info('moved {}'.format(dest_filepath))
    logging.info('attach this text to the ETL card & move card to "Whole Collection Packaged at U"')


def cleanup_leftover_files(alias):
    root_simples, root_compounds = '{}_simples'.format(alias), '{}_compounds'.format(alias)
    leftover_folders = [root for root, dirs, files in os.walk('output') if os.path.split(root)[1] in (root_simples, root_compounds)]
    for folder in leftover_folders:
        shutil.rmtree(folder)


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
    make_zips(alias)
    move_zips_to_U(cdm_data_dir, alias)
    cleanup_leftover_files(alias)
    logging.info('finished {}'.format(alias))
