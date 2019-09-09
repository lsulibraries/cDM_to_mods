#! /usr/bin/env python3

from collections import namedtuple

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
