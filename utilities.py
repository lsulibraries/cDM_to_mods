#! /usr/bin/env python3
# coding=utf-8

import os
import subprocess
from collections import namedtuple
import logging
import io


from lxml import etree as ET
import openpyxl


def parse_xlsx_file(xlsx_file):
    xlsx_workbook = openpyxl.load_workbook(xlsx_file)
    nicks_tags_dict = make_names_tags(xlsx_workbook)
    collection_named_tuple = make_named_tuple(xlsx_workbook)
    nicks_names_dict = make_nicks_names(xlsx_workbook)
    return nicks_tags_dict, nicks_names_dict, collection_named_tuple


def make_names_tags(xlsx_workbook):
    mappings_sheet = xlsx_workbook.get_sheet_by_name('Mappings')
    nicks_to_tags_dict = {shorten_name(row[0].value): row[1].value for row in mappings_sheet.iter_rows()}
    return nicks_to_tags_dict


def make_named_tuple(xlsx_workbook):
    items_sheet = xlsx_workbook.get_sheet_by_name('Descriptive Metadata')
    max_columns = count_active_columns(items_sheet)

    items_metadata = dict()
    for row_num, row in enumerate(items_sheet.iter_rows(max_col=max_columns)):
        if row_num == 0:
            headers = (shorten_name(i.value) for i in row)
            ItemMetadata = namedtuple('ItemMetadata', headers)
            continue
        values = (i.value for i in row)
        item = ItemMetadata(*values)
        items_metadata[row_num + 1] = item  # 1 indexing so that key matches spreadsheet row number
    return items_metadata


def make_nicks_names(xlsx_workbook):
    items_sheet = xlsx_workbook.get_sheet_by_name('Descriptive Metadata')
    max_columns = count_active_columns(items_sheet)
    for num, row in enumerate(items_sheet.iter_rows(max_col=max_columns)):
        if num == 0:
            return {shorten_name(i.value): i.value for i in row if i}


def shorten_name(fullname):
    return ''.join([i for i in fullname if i.isalnum()])


def count_active_columns(worksheet):
    row_1 = [i for i in worksheet.iter_rows(min_row=1, max_row=1)][0]
    return len({cell.value for cell in row_1}) - 1


def fix_permissions():
    all_files = [
        os.path.join(root, file)
        for root, dirs, files in os.walk('../cDM_to_mods')
        for file in files
    ]
    all_dirs = [
        os.path.join(root, dir)
        for root, dirs, files in os.walk('../cDM_to_mods')
        for dir in dirs
    ]
    for file in all_files:
        subprocess.run(['chmod', '664', file])
    for dir in all_dirs:
        subprocess.run(['chmod', '775', dir])


def setup_logging():
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    logging.basicConfig(filename='log.txt',
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


class MonographTitleCombiner:
    def __init__(self, alias_data_dir):
        self.alias_data_dir = alias_data_dir
        self.monograph_pointer_newtitle = dict()
        self.current_stucture_file = None
        self.main()

    def main(self):
        structure_files = [os.path.join(root, file)
                           for root, dirs, files in os.walk(self.alias_data_dir)
                           for file in files
                           if "_cpd.xml" in file]
        for structure_file in sorted(structure_files):
            self.current_stucture_file = structure_file
            parsed_structure_file = ET.parse(structure_file)
            root_elem = parsed_structure_file.getroot()
            self.make_pointer_new_monograph_title_dict(root_elem)

    def make_pointer_new_monograph_title_dict(self, root_elem):
        if root_elem.find('type').text != "Monograph":
            # Only Monograph types should continue, others exit out now.
            return
        assert self.children_meet_expectations(root_elem,
                                               expected_elems=('type', 'node'),
                                               silent_elems=('node', ))
        node_elems = [child for child in root_elem.iterchildren() if child.tag == 'node']
        for node_elem in node_elems:
            self.loop_one_layer(node_elem)

    def loop_one_layer(self, elem):
        child_node_elems = [child for child in elem.iterchildren() if child.tag == 'node']
        child_page_elems = [child for child in elem.iterchildren() if child.tag == 'page']
        if child_node_elems and not child_page_elems:
            assert self.children_meet_expectations(elem,
                                                   expected_elems=('nodetitle', 'node', 'page'),
                                                   silent_elems=('node', ),)
            for child in child_node_elems:
                self.loop_one_layer(child)
        elif child_page_elems and not child_node_elems:
            self.page_node_bunch(elem)
        else:
            raise Exception('Error:  a page and node on the same level {}'.format(self.current_stucture_file))

    def page_node_bunch(self, node_elem):
        elem_nodetitle = self.get_this_level_nodetitle(node_elem)
        page_elems = [elem for elem in node_elem.iterchildren() if elem.tag == 'page']
        for page_elem in page_elems:
            assert self.children_meet_expectations(page_elem,
                                                   expected_elems=('pageptr', 'pagefile', 'pagetitle'),
                                                   unique_elems=('pageptr', 'pagefile', 'pagetitle'),)
            pointer = page_elem.find('pageptr').text
            title = page_elem.find('pagetitle').text
            if elem_nodetitle:
                new_title = '{} - {}'.format(elem_nodetitle, title)
            else:
                new_title = title
            self.monograph_pointer_newtitle[pointer] = new_title

    def get_this_level_nodetitle(self, elem):
        nodetitle_elem = elem.find('nodetitle')
        if nodetitle_elem is not None:
            return nodetitle_elem.text
        raise Exception('No nodetitle at this level {} {}'.format(elem.tag, self.current_stucture_file))

    def children_meet_expectations(self, elem, expected_elems=[], silent_elems=[], unique_elems=[]):
        unique_set = set()
        for child in elem.iterchildren():
            if child.tag not in expected_elems:
                raise Exception('Unexpected node tag {} {}'.format(child.tag, self.current_stucture_file))
            if child.tag in silent_elems and self.has_text(child):
                raise Exception('Not capturing data in {} {} {}'.format(child.tag, child.text, self.current_stucture_file))
            if child.tag in unique_elems and child.tag in unique_set:
                raise Exception('Duplicate tag {} {}'.format(child.tag, self.current_stucture_file))
            else:
                unique_set.add(child.tag)
        return True

    @staticmethod
    def has_text(elem):
        return elem.text and isinstance(elem.text, str) and len(elem.text.strip()) > 0