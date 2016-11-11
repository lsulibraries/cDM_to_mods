#! /usr/bin/python3

import os
import sys
from shutil import copyfile
import subprocess
import datetime
import re
import csv
import json
from copy import deepcopy
import logging

from lxml import etree as ET

from post_conversion_cleanup import IsCountsCorrect

MODS_DEF = ET.parse('schema/mods-3-6.xsd')
MODS_SCHEMA = ET.XMLSchema(MODS_DEF)


def convert_to_mods(alias):
    cdm_data_dir = os.path.realpath(os.path.join(SOURCE_DIR, alias))
    nicks_to_names_dict = make_nicks_to_names(cdm_data_dir)
    mappings_dict = parse_mappings_file(alias)

    cdm_data_filestructure = [(root, dirs, files) for root, dirs, files in os.walk(cdm_data_dir)]
    simple_pointers, cpd_parent_pointers = parse_root_cdm_pointers(cdm_data_filestructure)

    parents_children = dict()
    for cpd_parent in cpd_parent_pointers:
        cpd_parent_filepath = os.path.join(cdm_data_dir, 'Cpd', '{}_cpd.xml'.format(cpd_parent))
        cpd_parent_etree = ET.parse(cpd_parent_filepath)
        children_pointers = [i.text for i in cpd_parent_etree.findall('.//pageptr')]
        parents_children[cpd_parent] = children_pointers

    remove_previous_mods(alias)

    for pointer in simple_pointers:
        output_path = os.path.join('output', '{}_simples'.format(alias), 'original_format')
        target_file = '{}.json'.format(pointer)
        path_to_pointer = [os.path.join(root, target_file)
                           for root, dirs, files in cdm_data_filestructure
                           if target_file in files][0]
        os.makedirs(output_path, exist_ok=True)
        pointer_json = get_cdm_pointer_json(path_to_pointer)
        nicks_texts = parse_json(pointer, pointer_json)
        propers_texts = convert_nicks_to_propers(nicks_to_names_dict, nicks_texts)
        mods = make_pointer_mods(path_to_pointer, pointer, pointer_json, propers_texts, alias, mappings_dict)
        reorder_sequence(mods)
        mods_bytes = ET.tostring(mods, xml_declaration=True, encoding="utf-8", pretty_print=True)
        mods_string = mods_bytes.decode('utf-8')
        with open('{}/{}.xml'.format(output_path, pointer), 'w', encoding="utf-8") as f:
            f.write(mods_string)
    logging.info('finished preliminary mods: simples')

    for pointer, _ in parents_children.items():
        output_path = os.path.join('output', '{}_compounds'.format(alias), 'original_format', pointer)
        path_to_pointer = os.path.join(cdm_data_dir, 'Cpd', '{}.json'.format(pointer))
        os.makedirs(output_path, exist_ok=True)
        pointer_json = get_cdm_pointer_json(path_to_pointer)
        nicks_texts = parse_json(pointer, pointer_json)
        propers_texts = convert_nicks_to_propers(nicks_to_names_dict, nicks_texts)
        mods = make_pointer_mods(path_to_pointer, pointer, pointer_json, propers_texts, alias, mappings_dict)
        reorder_sequence(mods)
        mods_bytes = ET.tostring(mods, xml_declaration=True, encoding="utf-8", pretty_print=True)
        mods_string = mods_bytes.decode('utf-8')
        with open('{}/MODS.xml'.format(output_path, pointer), 'w', encoding="utf-8") as f:
            f.write(mods_string)
        copyfile(os.path.join(cdm_data_dir, 'Cpd', '{}_cpd.xml'.format(pointer)), os.path.join(output_path, 'structure.cpd'))

    for parent, children_pointers in parents_children.items():
        for pointer in children_pointers:
            output_path = os.path.join('output', '{}_compounds'.format(alias), 'original_format', parent, pointer)
            path_to_pointer = os.path.join(cdm_data_dir, 'Cpd', parent, '{}.json'.format(pointer))
            os.makedirs(output_path, exist_ok=True)
            pointer_json = get_cdm_pointer_json(path_to_pointer)
            nicks_texts = parse_json(pointer, pointer_json)
            propers_texts = convert_nicks_to_propers(nicks_to_names_dict, nicks_texts)
            mods = make_pointer_mods(path_to_pointer, pointer, pointer_json, propers_texts, alias, mappings_dict)
            reorder_sequence(mods)
            mods_bytes = ET.tostring(mods, xml_declaration=True, encoding="utf-8", pretty_print=True)
            mods_string = mods_bytes.decode('utf-8')
            with open('{}/MODS.xml'.format(output_path, pointer), 'w', encoding="utf-8") as f:
                f.write(mods_string)
    logging.info('finished preliminary mods: compounds')

    polish_mods(alias)
    IsCountsCorrect(alias, SOURCE_DIR)
    logging.info('completed')
    logging.info('Your output files are in:  output/{}_simple/final_format/ and output/{}_compounds/final_format/'.format(alias, alias))


def polish_mods(alias):
    alias_xslts = read_alias_xslt_file(alias)

    simples_output_dir = os.path.join('output', '{}_simples'.format(alias))
    if '{}_simples'.format(alias) in os.listdir('output') and 'original_format' in os.listdir(simples_output_dir):
        flatten_simple_dir(simples_output_dir)
        run_saxon(simples_output_dir, alias_xslts, 'simple')
        flat_final_dir = os.path.join(simples_output_dir, 'final_format')
        validate_mods(alias, flat_final_dir)
        check_date_format(alias, flat_final_dir)
    else:
        logging.info('no simple objects in this collection')

    compounds_output_dir = os.path.join('output', '{}_compounds'.format(alias))
    if '{}_compounds'.format(alias) in os.listdir('output') and 'original_format' in os.listdir(compounds_output_dir):
        cpd_output_dir = os.path.join('output', '{}_compounds'.format(alias))
        flatten_cpd_dir(cpd_output_dir)
        run_saxon(cpd_output_dir, alias_xslts, 'compound')
        flat_final_dir = os.path.join(cpd_output_dir, 'post-saxon')
        validate_mods(alias, flat_final_dir)
        check_date_format(alias, flat_final_dir)
        reinflate_cpd_dir(cpd_output_dir)
    else:
        logging.info('no compound objects in this collection')


def remove_previous_mods(alias):
    xml_files = ['{}/{}'.format(root, file)
                 for root, dirs, files in os.walk('output')
                 for file in files
                 if alias in root and ".xml" in file]
    for file in xml_files:
        os.remove(file)


def validate_mods(alias, directory):
    all_passed = True
    xml_files = [file for file in os.listdir(directory) if ".xml" in file]
    for file in xml_files:
        file_etree = ET.parse(os.path.join(directory, file))
        pointer = file.split('.')[0]
        if not MODS_SCHEMA.validate(file_etree):
            all_passed = False
            logging.warning("{} {} post-xsl did not validate!!!!".format(alias, pointer))
    if all_passed:
        logging.info("This group of files post-xsl Validated")


def read_alias_xslt_file(alias):
    with open(os.path.join('alias_xslts', '{}.txt'.format(alias)), 'r') as f:
        return [i for i in f.read().split('\n')]


def flatten_simple_dir(simple_dir):
    source_dir = os.path.join(simple_dir, 'original_format')
    flattened_dir = os.path.join(simple_dir, 'presaxon_flattened')
    os.makedirs(flattened_dir, exist_ok=True)
    for file in os.listdir(source_dir):
        if '.xml' in file:
            copyfile(os.path.join(source_dir, file), os.path.join(flattened_dir, file))


def run_saxon(output_dir, alias_xslts, cpd_or_simple):
    starting_dir = os.path.join(output_dir, 'presaxon_flattened')
    for xslt in alias_xslts:
        logging.info('doing {} saxon {}'.format(cpd_or_simple.title(), xslt))
        new_dir = os.path.join(output_dir, xslt)
        os.makedirs(new_dir, exist_ok=True)
        path_to_xslt = os.path.join('xsl', '{}.xsl'.format(xslt))
        subprocess.call(['java',
                         '-jar',
                         'saxon9he.jar',
                         '-s:{}'.format(starting_dir),
                         '-xsl:{}'.format(path_to_xslt),
                         '-o:{}'.format(new_dir)])
        starting_dir = new_dir
    else:
        os.makedirs(os.path.join(output_dir, 'post-saxon'), exist_ok=True)
        for file in os.listdir(os.path.join(output_dir, xslt)):
            copyfile(os.path.join(output_dir, xslt, file), os.path.join(output_dir, 'post-saxon', file))
        if cpd_or_simple == 'simple':
            os.makedirs(os.path.join(output_dir, 'final_format'), exist_ok=True)
            for file in os.listdir(os.path.join(output_dir, xslt)):
                copyfile(os.path.join(output_dir, 'post-saxon', file), os.path.join(output_dir, 'final_format', file))


def flatten_cpd_dir(cpd_dir):
    source_dir = os.path.join(cpd_dir, 'original_format')
    flattened_dir = os.path.join(cpd_dir, 'presaxon_flattened')
    os.makedirs(flattened_dir, exist_ok=True)
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if ".xml" in file:
                source_folder_name = os.path.split(root)[-1]
                dest_filepath = os.path.join(flattened_dir, '{}.xml'.format(source_folder_name))
                copyfile(os.path.join(root, file), dest_filepath)


def reinflate_cpd_dir(cpd_dir):
    original_format_path = os.path.join(cpd_dir, 'original_format')
    original_format = [(root, dirs, files) for root, dirs, files in os.walk(original_format_path)]
    for file in os.listdir(os.path.join(cpd_dir, 'post-saxon')):
        for root, dirs, files in original_format:
            if file.split('.')[0] == os.path.split(root)[-1]:
                source_file = os.path.join(cpd_dir, 'post-saxon', file)
                dest_path = root.replace('original_format', 'final_format')
                os.makedirs(dest_path, exist_ok=True)
                dest_file = os.path.join(dest_path, 'MODS.xml')
                copyfile(source_file, dest_file)
    for root, dirs, files in original_format:
        if 'structure.cpd' in files:
            source_file = os.path.join(root, 'structure.cpd')
            dest_file = os.path.join(root.replace('original_format', 'final_format'), 'structure.cpd')
            copyfile(source_file, dest_file)


def make_nicks_to_names(cdm_data_dir):
    filepath = os.path.join(cdm_data_dir, 'Collection_Fields.json')
    json_text = get_cdm_pointer_json(filepath)
    nicks_names = parse_collection_fields('Collection_Fields', json_text)
    return nicks_names


def parse_collection_fields(filename, json_text):
    try:
        parsed_json = json.loads(json_text)
    except json.decoder.JSONDecodeError:
        logging.warning('{}.json is improperly formed json.  Conversion halted!'.format(filename))
        quit()
    return {field['nick']: field['name'] for field in parsed_json}


def parse_mappings_file(alias):
    with open('mappings_files/{}.csv'.format(alias), 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=',')
        return {i: j for i, j in csv_reader}


def parse_root_cdm_pointers(cdm_data_filestructure):
    Elems_ins = [os.path.join(root, file)
                 for root, dirs, files in cdm_data_filestructure
                 for file in files
                 if ("Elems_in_Collection" in file and ".json" in file)]
    simple_pointers, cpd_parent_pointers = [], []
    duplicates = []
    for filename in Elems_ins:
        json_text = get_cdm_pointer_json(filename)
        nicks_text = parse_json(filename, json_text)
        for i in nicks_text['records']:
            pointer = str(i['pointer'] or i['dmrecord'])
            if i['filetype'] == 'cpd':
                cpd_parent_pointers.append(pointer)
            else:
                if pointer in simple_pointers:
                    duplicates.append(pointer)
                simple_pointers.append(pointer)
    return simple_pointers, cpd_parent_pointers


def get_cdm_pointer_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_json(filename, json_text):
    try:
        parsed_alias_json = json.loads(json_text)
    except json.decoder.JSONDecodeError:
        logging.warning('{}.json is improperly formed json.  Conversion halted!'.format(filename))
        quit()
    return {nick: text for nick, text in parsed_alias_json.items()}


def convert_nicks_to_propers(nicks_to_names_dict, nicks_texts):
    propers_texts = dict()
    for k, v in nicks_texts.items():
        if k in nicks_to_names_dict:
            propers_texts[nicks_to_names_dict[k]] = v
    return propers_texts


def make_pointer_mods(path_to_pointer, pointer, pointer_json, propers_texts, alias, mappings_dict):
    NSMAP = {None: "http://www.loc.gov/mods/v3",
             'mods': "http://www.loc.gov/mods/v3",
             'xsi': "http://www.w3.org/2001/XMLSchema-instance",
             'xlink': "http://www.w3.org/1999/xlink", }
    root_element = ET.Element("mods", nsmap=NSMAP)

    for k, v in mappings_dict.items():
        if k in propers_texts and propers_texts[k]:
            replacement = propers_texts[k]
            for a, b in [('&', '&amp;'),
                         ('"', '&quot;'),
                         ('<', '&lt;'),
                         ('>', '&gt;')]:
                replacement = replacement.replace(a, b)
            v = v.replace("%value%", replacement)
            new_element = ET.fromstring(v)
            root_element.append(new_element)
        elif 'null' in k:
            new_element = ET.fromstring(v)
            if 'CONTENTdmData' in v:
                make_contentDM_elem(new_element[0], pointer, pointer_json, alias)
            root_element.append(new_element)

    id_elem = ET.Element("identifier", attrib={'type': 'uri', 'invalid': 'yes', 'displayLabel': "Migrated From"})
    id_elem.text = 'http://cdm16313.contentdm.oclc.org/cdm/singleitem/collection/{}/id/{}'.format(alias, pointer)
    root_element.append(id_elem)

    merge_same_fields(root_element)
    careful_tag_split(root_element, 'name', 'namePart')
    careful_tag_split(root_element, 'subject', 'topic')
    careful_tag_split(root_element, 'subject', 'geographic')
    careful_tag_split(root_element, 'subject', 'temporal')
    careful_tag_split(root_element, 'subject', 'hierarchicalGeographic')
    normalize_date(root_element, pointer)
    delete_empty_fields(root_element)
    reorder_sequence(root_element)

    return root_element


def reorder_sequence(root_element):
    if root_element.find('./location') is None:  # lxml wants this syntax
        return
    location_elem = root_element.find('./location')
    order_dict = {"physicalLocation": 0,
                  "shelfLocator": 1,
                  "url": 2,
                  "holdingSimple": 3,
                  "holdingExternal": 4, }
    child_elems = location_elem.getchildren()
    detached_list = sorted(child_elems, key=lambda x: order_dict[x.tag])
    for child in location_elem:
        location_elem.remove(child)
    for i in detached_list:
        location_elem.append(i)


def make_contentDM_elem(cdm_elem, pointer, pointer_json, alias):
    alias_elem = ET.Element('alias')
    alias_elem.text = alias
    cdm_elem.append(alias_elem)
    pointer_elem = ET.Element('pointer')
    pointer_elem.text = pointer
    cdm_elem.append(pointer_elem)
    dmGetItemInfo_elem = ET.Element('dmGetItemInfo', attrib={
        'mimetype': "application/json",
        'source': "https://server16313.contentdm.oclc.org/dmwebservices/index.php?q=dmGetItemInfo/{}/{}/json".format(alias, pointer),
        'timestamp': '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()), })
    dmGetItemInfo_elem.text = pointer_json
    cdm_elem.append(dmGetItemInfo_elem)


def careful_tag_split(etree, parent_tag_name, child_tag_name):
    # we split the child_tag text into pieces
    # and create a duplicate parent_tag object for each split child_tag text
    for name_elem in etree.findall('.//{}'.format(parent_tag_name)):
        remove_orig_parent = False
        for child in name_elem.getchildren():
            if child.tag == child_tag_name:
                remove_orig_parent = True
                for split in child.text.split(';'):
                    split = split.strip()
                    if not len(split):
                        continue
                    new_child_elem = deepcopy(child)
                    new_child_elem.text = split.strip()
                    copied_name_elem = deepcopy(name_elem)
                    for i in copied_name_elem:
                        if i.tag == child_tag_name:
                            copied_name_elem.remove(i)
                    copied_name_elem.insert(0, new_child_elem)
                    name_elem.getparent().append(copied_name_elem)
        if remove_orig_parent:
            etree.remove(name_elem)


year_month_day = re.compile(r'^(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})$')     # 1234-56-78 or 1234-5-6
year_last = re.compile(r'^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$')      # 12-34-5678 or 1-2-3456
year_only = re.compile(r'^(\d{4})$')                                  # 1234
year_month = re.compile(r'^(\d{4})[/.-](\d{1,2})$')                      # 1234-56 or 1234-5

correct_year_month_day = re.compile(r'^(\d{4})[/.-](\d{2})[/.-](\d{2})$')     # 1234-5-6
correct_year_last = re.compile(r'^(\d{2})[/.-](\d{2})[/.-](\d{4})$')      # 1-2-3456
correct_year_month = re.compile(r'^(\d{4})[/.-](\d{2})$')                      # 1234-5


def normalize_date(root_elem, pointer):
    date_elems = [i for tag in ('dateCaptured', 'recordChangeDate', 'recordCreationDate', 'dateIssued')
                  for i in root_elem.findall('.//{}'.format(tag))]
    for i in date_elems:
        i.text = i.text.strip()
        yearmonthday = year_month_day.search(i.text)
        yearlast = year_last.search(i.text)
        yearonly = year_only.search(i.text)
        yearmonth = year_month.search(i.text)

        if yearmonthday:
            year = yearmonthday.group(1)
            month = yearmonthday.group(2)
            day = yearmonthday.group(3)
            if len(month) == 1:
                month = '0{}'.format(month)
            if len(day) == 1:
                day = '0{}'.format(day)
            i.text = '{}-{}-{}'.format(year, month, day)
        elif yearlast:
            year = yearlast.group(3)
            month = yearlast.group(1)
            day = yearlast.group(2)
            if len(month) == 1:
                month = '0{}'.format(month)
            if len(day) == 1:
                day = '0{}'.format(day)
            i.text = '{}-{}-{}'.format(year, month, day)
        elif yearmonth:
            year = yearmonth.group(1)
            month = yearmonth.group(2)
            if len(month) == 1:
                month = '0{}'.format(month)
            i.text = '{}-{}'.format(year, month)
        elif yearonly:
            i.text = yearonly.group()


def check_date_format(alias, flat_final_dir):
    item_xml_files = [os.path.join(root, file) for root, dirs, files in os.walk(flat_final_dir)
                      for file in files if '.xml' in file]
    for file in item_xml_files:
        with open(file, 'r', encoding='utf-8') as f:
            file_text = bytes(bytearray(f.read(), encoding='utf-8'))
            file_etree = ET.fromstring(file_text)
        date_elems = [i for tag in ('dateCaptured', 'recordChangeDate', 'recordCreationDate', 'dateIssued')
                      for i in file_etree.findall('.//{}'.format(tag))]
        for i in date_elems:
            i.text = i.text.strip().replace('[', '').replace(']', '')
            yearmonthday = correct_year_month_day.search(i.text)
            yearonly = correct_year_last.search(i.text)
            yearmonth = correct_year_month.search(i.text)
            if not (yearmonthday or yearonly or yearmonth):
                logging.warning('{}.json has date "{}"'.format(file, i.text))


def merge_same_fields(orig_etree):
    for elem in orig_etree:
        for following_elem in elem.itersiblings():
            if elem.tag == following_elem.tag and elem.attrib == following_elem.attrib:
                for child in following_elem.iterchildren():
                    elem.insert(-1, child)
    return orig_etree


def delete_empty_fields(orig_etree):
    elems_list = [i for i in orig_etree]
    for elem in elems_list:
        if not elem.text and len(elem) == 0:
            orig_etree.remove(elem)
    return orig_etree


def setup_logging():
    logging.basicConfig(filename='convert_to_mods_log.txt',
                        level=logging.INFO,
                        format='%(asctime)s: %(levelname)-8s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def write_etree(etree, name):
    os.makedirs('debug_output_xmls', exist_ok=True)
    with open('debug_output_xmls/{}.xml'.format(name), 'w') as f:
        mods_bytes = ET.tostring(etree, xml_declaration=True, encoding="utf-8", pretty_print=True)
        mods_string = mods_bytes.decode('utf-8')
        f.write(mods_string)


if __name__ == '__main__':
    setup_logging()
    try:
        alias = sys.argv[1]
        SOURCE_DIR = sys.argv[2]
    except IndexError:
        logging.warning('')
        logging.warning('Change to: "python convert_to_mods.py $aliasname $path/to/Cached_Cdm_files"')
        logging.warning('')
        quit()
    logging.info('starting {}'.format(alias))
    convert_to_mods(alias)
    logging.info('finished {}'.format(alias))
