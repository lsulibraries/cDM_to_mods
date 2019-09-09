#! /usr/bin/env python3

import os
import sys
import re
from shutil import copyfile
import subprocess
import datetime
from copy import deepcopy
import logging

from lxml import etree as ET

from utilities import parse_xlsx_file


# from post_conversion_cleanup import IsCountsCorrect


MODS_DEF = ET.parse('schema/mods-3-6.xsd')
MODS_SCHEMA = ET.XMLSchema(MODS_DEF)


def convert_to_mods(xlsx_file):
    alias = os.path.splitext(os.path.split(xlsx_file)[-1])[0]
    remove_previous_mods(alias)
    mappings_dict, nicks_names_dict, items_metadata = parse_xlsx_file(xlsx_file)
    simple_objects, cpd_objects = group_by_simple_cpd(items_metadata)
    print([i.Identifier for i in simple_objects])
    print([i.Identifier for f, g in cpd_objects.items() for i in g])
    for ItemMetadata in simple_objects:
        output_path = os.path.join('output', "{}_simples".format(alias), 'original_format')
        os.makedirs(output_path, exist_ok=True)
        output_file = "{}.xml".format(os.path.splitext(ItemMetadata.FileName)[0])
        output_filepath = os.path.join(output_path, output_file)
        make_a_single_mods(ItemMetadata, alias, mappings_dict, nicks_names_dict, output_filepath)
    logging.info('finished preliminary mods: simples')
    for parent, child_objects in cpd_objects.items():
        parent_ItemMetadata = [i for i in child_objects if i.Directory == i.Identifier]
        for ItemMetadata in parent_ItemMetadata:
            parent_pointer = str(ItemMetadata.Directory)
            output_path = os.path.join('output', "{}_compounds".format(alias), 'original_format', parent_pointer)
            os.makedirs(output_path, exist_ok=True)
            output_file = "{}.xml".format(parent_pointer)
            output_filepath = os.path.join(output_path, output_file)
            make_a_single_mods(ItemMetadata, alias, mappings_dict, nicks_names_dict, output_filepath)
        for ItemMetadata in child_objects:
            if str(ItemMetadata.Identifier) == str(ItemMetadata.Directory):
                continue
            parent_pointer = str(ItemMetadata.Directory)
            child_pointer = str(ItemMetadata.Identifier)
            output_path = os.path.join('output', "{}_compounds".format(alias), 'original_format', parent_pointer, child_pointer)
            os.makedirs(output_path, exist_ok=True)
            output_file = "{}.xml".format(os.path.splitext(ItemMetadata.FileName)[0])
            output_filepath = os.path.join(output_path, output_file)
            make_a_single_mods(ItemMetadata, alias, mappings_dict, nicks_names_dict, output_filepath)
        logging.info('finished preliminary mods: compounds')

    saxon_n_cleanup_mods(alias)
    # IsCountsCorrect(alias, cdm_data_dir)
    logging.info('completed')
    logging.info('Your output files are in:  output/{}_simple/final_format/ and output/{}_compounds/final_format/'.format(alias, alias))


def make_a_single_mods(ItemMetadata, alias, mappings_dict, nicks_names_dict, output_filepath):
    mods = build_xml(ItemMetadata, mappings_dict, nicks_names_dict)
    merge_same_fields(mods)
    careful_tag_split(mods, 'name', 'namePart')
    for sub_subject in ('topic', 'geographic', 'temporal'):
        careful_tag_split(mods, 'subject', sub_subject)
    for sub_subject in ("continent", "country", "province", "region", "state", "territory", "county", "city", "citySection", "island", "area"):
        careful_tag_split(mods, 'hierarchicalGeographic', sub_subject)
    delete_empty_fields(mods)
    reorder_title(mods)
    reorder_location(mods)

    mods_bytes = ET.tostring(mods, xml_declaration=True, encoding="utf-8", pretty_print=True)
    mods_string = mods_bytes.decode('utf-8')
    with open(output_filepath, 'w', encoding="utf-8") as f:
        f.write(mods_string)


def build_xml(ItemMetadata, mappings_dict, nicks_names_dict):
    NSMAP = {None: "http://www.loc.gov/mods/v3",
             'mods': "http://www.loc.gov/mods/v3",
             'xsi': "http://www.w3.org/2001/XMLSchema-instance",
             'xlink': "http://www.w3.org/1999/xlink", }
    root_element = ET.Element("mods", nsmap=NSMAP)
    for k, v in mappings_dict.items():
        try:
            replacement = getattr(ItemMetadata, k)
        except AttributeError:
            continue
        if not replacement:
            continue
        elif isinstance(replacement, datetime.datetime):
            replacement = replacement.strftime('%Y-%m-%d')
        else:
            replacement = str(replacement)
            for a, b in [('&', '&amp;'),
                         ('"', '&quot;'),
                         ('<', '&lt;'),
                         ('>', '&gt;')]:
                replacement = replacement.replace(a, b)
        v = v.replace("%value%", replacement)
        new_element = ET.fromstring(v)
        root_element.append(new_element)
    return root_element


def group_by_simple_cpd(items_metadata):
    simple_objects, compound_objects = set(), dict()
    for identifier, ItemMetadata in items_metadata.items():
        if ItemMetadata.Child:
            if ItemMetadata.Directory not in compound_objects:
                compound_objects[ItemMetadata.Directory] = {ItemMetadata, }
            else:
                compound_objects[ItemMetadata.Directory].add(ItemMetadata)
    for identifier, ItemMetadata in items_metadata.items():
        if ItemMetadata.Directory in compound_objects:
            compound_objects[ItemMetadata.Directory].add(ItemMetadata)
        else:
            simple_objects.add(ItemMetadata)
    return simple_objects, compound_objects


def remove_previous_mods(alias):
    xml_files = ['{}/{}'.format(root, file)
                 for root, dirs, files in os.walk('output')
                 for file in files
                 if alias in root and ".xml" in file]
    for file in xml_files:
        os.remove(file)


def merge_same_fields(orig_etree):
    for elem in orig_etree:
        for following_elem in elem.itersiblings():
            if elem.tag == following_elem.tag and elem.attrib == following_elem.attrib:
                for child in following_elem.iterchildren():
                    elem.insert(-1, child)
    return orig_etree


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
                    new_child_elem.text = split
                    copied_name_elem = deepcopy(name_elem)
                    for i in copied_name_elem:
                        if i.tag == child_tag_name:
                            copied_name_elem.remove(i)
                    copied_name_elem.insert(0, new_child_elem)
                    name_elem.getparent().append(copied_name_elem)
        if remove_orig_parent:
            name_elem.getparent().remove(name_elem)


def delete_empty_fields(orig_etree):
    elems_list = [i for i in orig_etree]
    for elem in elems_list:
        if not elem.text and len(elem) == 0:
            orig_etree.remove(elem)
    return orig_etree


def reorder_title(root_element):
    subtag_order_dict = {"nonSort": 0,
                         "title": 1,
                         "subTitle": 2,
                         "partNumber": 3,
                         "partName": 4, }
    target_tagname = 'titleInfo'
    reorder_node(root_element, target_tagname, subtag_order_dict)


def reorder_location(root_element):
    subtag_order_dict = {"physicalLocation": 0,
                         "shelfLocator": 1,
                         "url": 2,
                         "holdingSimple": 3,
                         "holdingExternal": 4, }
    target_tagname = 'location'
    reorder_node(root_element, target_tagname, subtag_order_dict)


def reorder_node(root_element, target_tagname, subtag_order_dict):
    if root_element.find('./{}'.format(target_tagname)) is None:  # lxml wants this syntax
        return
    location_elem = root_element.find('./{}'.format(target_tagname))
    child_elems = location_elem.getchildren()
    detached_list = sorted(child_elems, key=lambda x: subtag_order_dict[x.tag])
    for child in location_elem:
        location_elem.remove(child)
    for i in detached_list:
        location_elem.append(i)


def saxon_n_cleanup_mods(alias):
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


def read_alias_xslt_file(alias):
    with open(os.path.join('alias_xslts', '{}.txt'.format(alias)), 'r') as f:
        return [i for i in f.read().split('\n')]


def flatten_simple_dir(simple_dir):
    orig_format_dir = os.path.join(simple_dir, 'original_format')
    flattened_dir = os.path.join(simple_dir, 'presaxon_flattened')
    os.makedirs(flattened_dir, exist_ok=True)
    for file in os.listdir(orig_format_dir):
        if '.xml' in file:
            copyfile(os.path.join(orig_format_dir, file), os.path.join(flattened_dir, file))


def run_saxon(output_dir, alias_xslts, cpd_or_simple):
    starting_dir = os.path.join(output_dir, 'presaxon_flattened')
    alias_xslts = [i for i in alias_xslts if i]
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


def validate_mods(alias, directory):
    xml_files = [file for file in os.listdir(directory) if ".xml" in file]
    for file in xml_files:
        file_etree = ET.parse(os.path.join(directory, file))
        pointer = file.split('.')[0]
        if not MODS_SCHEMA.validate(file_etree):
            logging.warning("{} {} post-xsl did not validate!!!!".format(alias, pointer))
            break
    else:
        logging.info("This group of files post-xsl Validated")


def check_date_format(alias, flat_final_dir):
    item_xml_files = [os.path.join(root, file) for root, dirs, files in os.walk(flat_final_dir)
                      for file in files if '.xml' in file]
    for file in item_xml_files:
        file_etree = ET.parse(file)
        date_elems = [elem for tag in ('dateCaptured', 'recordChangeDate', 'recordCreationDate', 'dateIssued', 'dateCreated',)
                      for elem in file_etree.findall('.//{{http://www.loc.gov/mods/v3}}{}'.format(tag))]
        for i in date_elems:
            if not good_format_date(i.text):
                logging.warning('{} {} has bad date: "{}"'.format(file, i.tag.replace('{http://www.loc.gov/mods/v3}', ''), i.text))


correct_year_month_day = re.compile(r'^(\d{4})[-](\d{2})[-](\d{2})$')     # 1234-05-06
correct_year_only = re.compile(r'^(\d{4})$')                              # 3456
correct_year_month = re.compile(r'^(\d{4})[-](\d{2})$')                   # 1234-05


def good_format_date(text):
        yearmonthday = correct_year_month_day.search(text)
        yearonly = correct_year_only.search(text)
        yearmonth = correct_year_month.search(text)
        if (yearmonthday or yearonly or yearmonth):
            return True
        else:
            return False


def flatten_cpd_dir(cpd_dir):
    orig_format_dir = os.path.join(cpd_dir, 'original_format')
    flattened_dir = os.path.join(cpd_dir, 'presaxon_flattened')
    os.makedirs(flattened_dir, exist_ok=True)
    for root, dirs, files in os.walk(orig_format_dir):
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


def setup_logging():
    logging.basicConfig(filename='csv_to_mods_log.txt',
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
        collection_xlsx = sys.argv[1]
    except IndexError:
        logging.warning('')
        logging.warning('Change to: "python csv_to_mods.py $path/to/CollectionX.xlsx"')
        logging.warning('')
        quit()
    logging.info('starting {}'.format(collection_xlsx))
    convert_to_mods(collection_xlsx)
    logging.info('finished {}'.format(collection_xlsx))
