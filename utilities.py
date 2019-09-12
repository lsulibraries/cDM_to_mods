#! /usr/bin/env python3

import os
import subprocess
from collections import namedtuple
import logging
import io

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
    for num, row in enumerate(items_sheet.iter_rows(max_col=max_columns)):
        if num == 0:
            headers = (shorten_name(i.value) for i in row)
            ItemMetadata = namedtuple('ItemMetadata', headers)
            continue
        values = (i.value for i in row)
        item = ItemMetadata(*values)
        items_metadata[item.Identifier] = item
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
