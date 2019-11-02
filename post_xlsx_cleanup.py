#! /usr/bin/env python3

import os
import sys
import shutil
import logging

from lxml import etree as ET

from utilities import parse_xlsx_file
from utilities import fix_permissions
from utilities import setup_logging
from utilities import group_by_simple_cpd


def main(xlsx_path):
    alias = os.path.splitext(os.path.split(xlsx_path)[-1])[0]
    _, metadata, _ = parse_xlsx_file(xlsx_path)
    simples, compounds = group_by_simple_cpd(metadata)
    pull_in_binaries(xlsx_path, simples, compounds)
    make_structurefiles(compounds, alias)
    report_filetype(alias)
    folder_by_extension(alias)
    make_zips(alias)
    cleanup_leftover_files(alias)
    fix_permissions()

def pull_in_binaries(xlsx_path, simples, compounds):
    source_root, xlsx_file = os.path.split(xlsx_path)
    alias = os.path.splitext(xlsx_file)[0]
    for metadata in simples:
        kind = 'simple'
        sourcepath = os.path.join(
            f"{metadata['Directory']}",
            metadata['FileName']
        )
        outroot = os.path.join(
            'output',
            f"{alias}_simples",
            'final_format'
        )
        copy_binary(kind, sourcepath, outroot)
    for parent, child_objects in compounds.items():
        for child, metadata in child_objects.items():
            if child == 'parent':  # parent root items have no binaries to move
                continue
            kind = 'compound'
            sourcepath = os.path.join(
                f"{metadata['Directory']}",
                metadata['FileName']
            )
            outroot = os.path.join(
                'output',
                f"{alias}_compounds",
                'final_format',
                f"{metadata['Parent']}",
                f"{metadata['Child']}"
            )
            copy_binary(kind, sourcepath, outroot)
    logging.info('PullInBinaries done')


def copy_binary(kind, sourcepath, outroot):
    sourcefile = os.path.split(sourcepath)[1]
    if kind == 'simple':
        outfile = sourcefile
    elif kind == 'compound':
        outfile = f"OBJ.{os.path.splitext(sourcefile)[1]}"
    try:
        shutil.copyfile(
            sourcepath,
            os.path.join(outroot, outfile)
        )
    except FileNotFoundError:
        logging.fatal(f"expecting file at {sourcepath} \n  Program cancelled")
        quit()


def make_structurefiles(compounds, alias):
    for parent, items in compounds.items():
        root_element = ET.Element("islandora_compound_object", title=f"{parent}")
        children = [int(i) for i in items if i != 'parent']
        for name in sorted(children):
            subelem = ET.Element("child", content=f"{parent}/{name}")
            root_element.append(subelem)
        xml_bytes = ET.tostring(root_element, xml_declaration=True, encoding="utf-8", pretty_print=True)
        xml_string = xml_bytes.decode('utf-8')
        with open(f"output/{alias}_compounds/final_format/{parent}/structure.xml", 'w', encoding="utf-8") as f:
            f.write(xml_string)

    logging.info('make_structurefiles done')


def report_filetype(alias):
    filetypes = set()
    all_binaries = []
    simples_binaries = ["{}/{}".format(root, file)
                        for root, _, files in os.walk('output/{}_simples/final_format'.format(alias))
                        for file in files
                        if '.xml' not in file]
    all_binaries.extend(simples_binaries)
    compounds_binaries = ["{}/{}".format(root, file)
                          for root, _, files in os.walk('output/{}_compounds/final_format'.format(alias))
                          for file in files
                          if '.xml' not in file]
    all_binaries.extend(compounds_binaries)
    for binary_filename in all_binaries:
        filetypes.add(binary_filename.split('.')[-1])
    logging.info(f"Collection contains filetypes: {filetypes}")


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
    root_simples, root_compounds = f"{alias}_simples", f"{alias}_compounds"
    leftover_folders = [
        root
        for root, _, files in os.walk('output')
        if os.path.split(root)[1] in (root_simples, root_compounds)]
    for folder in leftover_folders:
        shutil.rmtree(folder)
    logging.info('intermediate folders deleted')


if __name__ == '__main__':
    logging_string = setup_logging()
    try:
        xlsx_path = sys.argv[1]
    except IndexError:
        logging.warning('')
        logging.warning('Change to: "python post_xlsx_cleanup.py $path/to/{filename}.xlsx"')
        logging.warning('')
        quit()
    logging.info(f"starting {xlsx_path}")
    main(xlsx_path)
    logging.info(f"finished {xlsx_path}")
    logging_string.close()
