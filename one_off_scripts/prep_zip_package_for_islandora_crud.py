#! /usr/bin/env python3

import os
import shutil
import re
from shutil import copyfile

from lxml import etree as ET

MODS_DEF = ET.parse('../schema/mods-3-6.xsd')
MODS_SCHEMA = ET.XMLSchema(MODS_DEF)

print('got past schema connecting')


def main(intended_namespace,
         original_islandora_dir,
         revised_mods_dir):
    namespace = find_namespace(original_islandora_dir)
    new_islandora_dir = '/home/francis/Desktop/New_islandora_mods/{}'.format(namespace)
    os.makedirs(new_islandora_dir, exist_ok=True)

    pointer_pid = make_pointers_to_pid_dict(original_islandora_dir)

    zips_for_this_namespace = [os.path.join(root, file)
                               for root, dirs, files in os.walk(revised_mods_dir)
                               for file in files
                               if namespace in os.path.splitext(file)[0] and
                               os.path.splitext(file)[1] == '.zip']

    for zip_file in zips_for_this_namespace:
        os.makedirs(new_islandora_dir, exist_ok=True)
        if 'cpd' in zip_file:
            do_compounds(zip_file, new_islandora_dir, namespace, pointer_pid)
        else:
            do_simples(zip_file, new_islandora_dir, namespace, pointer_pid)
    validate_mods(namespace, new_islandora_dir)


def find_namespace(original_islandora_dir):
    accepted_namespace = ''
    for file in os.listdir(original_islandora_dir):
        found_namespace = file.split('_')[0]
        if accepted_namespace and found_namespace != accepted_namespace:
            print('the files in {} are not for the same namespace'.format(original_islandora_dir))
            quit()
        accepted_namespace = file.split('_')[0]
    return accepted_namespace


def make_pointers_to_pid_dict(original_islandora_dir):
    pointer_line_regex = re.compile('<pointer>([0-9]+)<\/pointer>')
    pointer_pid = dict()
    for root, dirs, files in os.walk(original_islandora_dir):
        for file in files:
            pid = file.split('_')[1]
            fullpath = os.path.join(root, file)
            with open(fullpath, 'r') as f:
                for line in f.readlines():
                    all_matches = pointer_line_regex.findall(line)
                    if all_matches:
                        pointer = all_matches[0]
                        pointer_pid[pointer] = pid
    return pointer_pid


def do_compounds(zip_file, new_islandora_dir, namespace, pointer_pid):
    tmp_cpd_dir = 'temp_cpd_dir'
    flat_cpd_dir = 'flat_cpd_xmls'
    os.makedirs(tmp_cpd_dir, exist_ok=False)
    os.makedirs(flat_cpd_dir, exist_ok=False)
    shutil.unpack_archive(zip_file, tmp_cpd_dir)
    flatten_cpd_dir(tmp_cpd_dir, flat_cpd_dir, namespace, pointer_pid)
    for file in os.listdir(flat_cpd_dir):
        new_filename = os.path.join(new_islandora_dir, file)
        shutil.copyfile(os.path.join(flat_cpd_dir, file), new_filename)
    shutil.rmtree(tmp_cpd_dir)
    shutil.rmtree(flat_cpd_dir)


def flatten_cpd_dir(source_dir, output_dir, namespace, pointer_pid):
    cpd_files = sorted([os.path.join(root, file)
                        for root, dirs, files in os.walk(source_dir)
                        for file in files
                        if os.path.split(file)[1] == 'MODS.xml'
                        ])
    for source_filepath in cpd_files:
        pointer = os.path.split(os.path.split(source_filepath)[0])[1]
        pid = switch_pointer_for_pid(pointer, pointer_pid)
        if not isinstance(pid, str):
            print("no match for pointer {}".format(pointer))
            print(pointer, pid)
            continue
        dest_filepath = os.path.join(output_dir, '{}_{}_MODS.xml'.format(namespace, pid))
        copyfile(source_filepath, dest_filepath)


def do_simples(zip_file, new_islandora_dir, namespace, pointer_pid):
    tmp_simple_dir = 'tmp_simple'
    os.makedirs(tmp_simple_dir, exist_ok=False)
    shutil.unpack_archive(zip_file, tmp_simple_dir)
    simples_files = sorted([os.path.join(root, file)
                            for root, dirs, files in os.walk(tmp_simple_dir)
                            for file in files
                            if os.path.splitext(file)[1] == '.xml'])
    for simple_file in simples_files:
        pointer = os.path.splitext(os.path.split(simple_file)[1])[0]
        pid = switch_pointer_for_pid(pointer, pointer_pid)
        if not isinstance(pid, str):
            print("no match for pointer {}".format(pointer))
            continue
        dest_path = os.path.join(new_islandora_dir, '{}_{}_MODS.xml'.format(namespace, pid))
        shutil.copyfile(simple_file, dest_path)
    shutil.rmtree(tmp_simple_dir)


def switch_pointer_for_pid(pointer, pointer_pid):
    return pointer_pid.get(pointer)


def validate_mods(namespace, directory):
    xml_files = [file for file in os.listdir(directory) if ".xml" in file]
    for file in xml_files:
        file_etree = ET.parse(os.path.join(directory, file))
        pointer = file.split('.')[0]
        if not MODS_SCHEMA.validate(file_etree):
            print("{} {} did not validate!!!!".format(namespace, pointer))
            break
    else:
        print("This group of files Validated")


if __name__ == '__main__':
    intended_namespace = 'lsuhsc-p15140coll50'
    original_islandora_dir = '/home/francis/Desktop/Original_from_islandora/{}'.format(intended_namespace)
    revised_mods_dir = '/home/francis/Desktop/For_CRUD'
    main(intended_namespace,
         original_islandora_dir,
         revised_mods_dir)
