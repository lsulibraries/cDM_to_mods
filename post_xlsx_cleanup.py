#! /usr/bin/env python3

import os
import sys
import shutil
import logging
import io

from lxml import etree as ET

from utilities import parse_xlsx_file


class IsCountsCorrect():
    def __init__(self, alias, binaries_dir, simples, parents, cpd_children):
        all_exp_simples, all_exp_parents, exp_child_dictionary = simples, parents, cpd_children
        all_exp_children = [i for key in exp_child_dictionary for i in exp_child_dictionary[key]]
        all_obs_simples = self.lookup_observed_simples(alias)
        all_obs_parents, all_obs_children = self.lookup_observed_compounds(alias)

        logging.info('Count Simples: {}'.format(len(all_exp_simples)))
        logging.info('Count Cpd Parents: {}'.format(len(all_exp_parents)))
        logging.info('Count Cpd Children: {}'.format(len(all_exp_children)))
        if len(all_obs_simples) == len(all_exp_simples):
            logging.info('simples metadata counts match')
        else:
            logging.warning("BIG DEAL:  Simples Don't Match.  Expected: {}.  Observed: {}".format(len(all_exp_simples), len(all_obs_simples)))
            quit()
        if len(all_exp_parents) == len(all_obs_parents):
            logging.info('compound parents metadata counts match')
        else:
            logging.warning("BIG DEAL:  Compound Parents Don't Match.  Expected: {}.  Observed: {}".format(len(all_exp_parents), len(all_obs_parents)))
            quit()
        if len(all_exp_children) == len(all_obs_children):
            logging.info('compound children metadata counts match')
        else:
            logging.warning("BIG DEAL:  Compound Children Don't Match.  Expected: {}.  Observed: {}".format(len(all_exp_children), len(all_obs_children)))
            quit()
        logging.info('IsCountsCorrect done')

    def lookup_observed_simples(self, alias):
        output_dir = os.path.join('output', '{}_simples'.format(alias), 'final_format')
        if not os.path.isdir(output_dir):
            return []
        simple_files = [i for i in os.listdir(output_dir) if os.path.splitext(i)[1] == ".xml"]
        return simple_files

    def lookup_observed_compounds(self, alias):
        output_dir = os.path.join('output', '{}_compounds'.format(alias), 'final_format')
        cpd_parents, cpd_children = [], []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                parent_dir = os.path.split(root)[0]
                grandparent_dir = os.path.split(parent_dir)[1]
                if file == "MODS.xml":
                    if grandparent_dir.isnumeric():
                        cpd_children.append(parent_dir)
                    else:
                        cpd_parents.append(parent_dir)
        return cpd_parents, cpd_children


class PullInBinaries():
    def __init__(self, alias, binaries_dir, simples, parents, cpd_children):
        for parent, child_objects in cpd_children.items():
            for ItemMetadata in child_objects:
                sourcefile = ItemMetadata.FileName
                sourcepath = os.path.join(binaries_dir, alias, str(ItemMetadata.Directory))
                kind = 'compound'
                outroot = 'output/{}_compounds/final_format/{}/{}'.format(alias, ItemMetadata.Directory, ItemMetadata.Identifier)
                if sourcefile:
                    self.copy_binary(kind, sourcepath, sourcefile, outroot)
        for ItemMetadata in simples:
            sourcefile = ItemMetadata.FileName
            sourcepath = os.path.join(binaries_dir, alias, str(ItemMetadata.Directory))
            kind = 'simple'
            outroot = 'output/{}_simples/final_format'.format(alias)
            self.copy_binary(kind, sourcepath, sourcefile, outroot)
        logging.info('PullInBinaries done')

    def makedict_sourcefiles(self, alias, binaries_dir):
        sourcefiles_paths = dict()
        input_dir = os.path.join(binaries_dir, alias)
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                filename, extension = os.path.splitext(file)
                if extension.lower() in ('.jp2', '.mp4', '.mp3', '.pdf', '.tif'):
                    if filename in sourcefiles_paths:
                        logging.warning("pointer {} has multiple possible source binaries -- please cull unwanted version".format(filename))
                        quit()
                    sourcefiles_paths[filename] = (root, file)
        return sourcefiles_paths

    def copy_binary(self, kind, sourcepath, sourcefile, outroot):
        if kind == 'simple':
            shutil.copyfile(os.path.join(sourcepath, sourcefile), os.path.join(outroot, sourcefile))
        elif kind == 'compound':
            shutil.copyfile(os.path.join(sourcepath, sourcefile), os.path.join(outroot, "OBJ.{}".format(sourcefile.split('.')[-1])))


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
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    logging.basicConfig(filename='post_csv_cleanup_log.txt',
                        level=logging.INFO,
                        format='%(asctime)s: %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging_string = io.StringIO()
    string_handler = logging.StreamHandler(logging_string)
    string_handler.setLevel(logging.DEBUG)
    string_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(string_handler)
    return logging_string


def folder_by_extension(alias):
    starting_folder = os.path.join('output', '{}_simples'.format(alias), 'final_format')
    if not os.path.isdir(starting_folder):
        return
    files = [i for i in os.listdir(starting_folder) if os.path.isfile(os.path.join(starting_folder, i))]
    extensions = {i.split(".")[1] for i in files if i.split(".")[1] != 'xml'}
    for extension in extensions:
        dest_folder = os.path.join(starting_folder, extension)
        if os.path.isdir(os.path.realpath(dest_folder)):
            shutil.rmtree(dest_folder)
        os.makedirs(dest_folder, exist_ok=True)
        files_limited_to_extension = {file.split('.')[0] for file in files if file.split('.')[1] == extension}
        files_with_extension_plus_samenames = [file for file in files if file.split('.')[0] in files_limited_to_extension]
        for file in files_with_extension_plus_samenames:
            shutil.copyfile(os.path.join(starting_folder, file), os.path.join(dest_folder, file))


def make_zips(alias):
    os.makedirs('Upload_to_Islandora', exist_ok=True)
    cpd_output = 'output/{}_compounds/final_format'.format(alias)
    if os.path.isdir(cpd_output):
        zipfilename = 'Upload_to_Islandora/{}-cpd'.format(alias)
        shutil.make_archive(zipfilename, 'zip', cpd_output)
        logging.info('{}.zip created'.format(zipfilename))

    simple_output = 'output/{}_simples/final_format'.format(alias)
    if os.path.isdir(simple_output):
        subdirs = [i for i in os.listdir(simple_output) if os.path.isdir(os.path.join(simple_output, i))]
        for subdir in subdirs:
            subdir_path = os.path.join(simple_output, subdir)
            zipfilename = 'Upload_to_Islandora/{}-{}'.format(alias, subdir)
            shutil.make_archive(zipfilename, 'zip', subdir_path)
            logging.info('{}.zip created'.format(zipfilename))


def cleanup_leftover_files(alias):
    root_simples, root_compounds = '{}_simples'.format(alias), '{}_compounds'.format(alias)
    leftover_folders = [root for root, dirs, files in os.walk('output') if os.path.split(root)[1] in (root_simples, root_compounds)]
    for folder in leftover_folders:
        shutil.rmtree(folder)
    logging.info('intermediate folders deleted')


def do_post_conversion(alias, binaries_dir):
    nicks_tags_dict, nicks_names_dict, items_metadata = parse_xlsx(binaries_dir, alias)
    simples, parents, cpd_children = split_source_metadata(items_metadata)
    PullInBinaries(alias, binaries_dir, simples, parents, cpd_children)
    # MakeStructureFile(alias)
    IsCountsCorrect(alias, binaries_dir, simples, parents, cpd_children)
    report_filetype(alias)
    folder_by_extension(alias)
    make_zips(alias)
    # cleanup_leftover_files(alias)


def split_source_metadata(items_metadata):
    simples, parents, cpd_children = [], [], dict()
    for identifier, ItemMetadata in items_metadata.items():
        if ItemMetadata.Child and ItemMetadata.Child != 'None':
            if ItemMetadata.Directory not in cpd_children:
                cpd_children[ItemMetadata.Directory] = [ItemMetadata]
            else:
                cpd_children[ItemMetadata.Directory].append(ItemMetadata)
    for identifier, ItemMetadata in items_metadata.items():
        if identifier in cpd_children:
            parents.append(ItemMetadata)
        elif not ItemMetadata.Child or ItemMetadata.Child == 'None':
            simples.append(ItemMetadata)
    return simples, parents, cpd_children


def parse_xlsx(binaries_dir, alias):
    xlsx_filepath = locate_xlsx_file(binaries_dir, alias)
    parsed_xlsx = parse_xlsx_file(xlsx_filepath)
    return parsed_xlsx


def locate_xlsx_file(binaries_dir, alias):
    xlsx_filepath = os.path.join(binaries_dir, '{}.xlsx'.format(alias))
    try:
        os.path.isfile(xlsx_filepath)
    except NameError:
        logging.warning('No file {}.xlsx found in source folder "{}"'.format(alias, binaries_dir))
        quit()
    return xlsx_filepath


if __name__ == '__main__':
    logging_string = setup_logging()
    try:
        alias = sys.argv[1]
        binaries_dir = sys.argv[2]
    except IndexError:
        logging.warning('')
        logging.warning('Change to: "python post_csv_cleanup.py $alias {}"'.format(os.path.join('$filepath', 'to', 'directory', 'with', 'the', 'binaries')))
        logging.warning('')
        quit()
    logging.info('starting {}'.format(alias))
    do_post_conversion(alias, binaries_dir)
    logging.info('finished {}'.format(alias))
    logging_string.close()
