#! /usr/bin/python3

import os
import sys
import datetime
import csv
from lxml import etree as ET
import json


def parse_root_cdm_pointers(cdm_data_filestructure):
    Elems_ins = [os.path.join(root, file)
                 for root, dirs, files in cdm_data_filestructure
                 for file in files
                 if ("Elems_in_Collection" in file and ".json" in file)]
    root_pointers = []
    for file in Elems_ins:
        with open(file, 'r') as f:
            parsed_json_elems_file = json.loads(f.read())
        for i in parsed_json_elems_file['records']:
            pointer = str(i['pointer'] or i['dmrecord'])
            root_pointers.append(pointer)
    return root_pointers


def parse_mappings_file(alias):
    with open('mappings_files/{}.csv'.format(alias), 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        return {i: j for i, j in csv_reader}


def get_cdm_pointer_json(filepath):
    with open(filepath, 'r') as f:
        return f.read()


def parse_cdm_pointer_json(pointer_json):
    parsed_alias_json = json.loads(pointer_json)
    return {nick: text for nick, text in parsed_alias_json.items()}


def make_nicks_to_names(cdm_data_dir):
    rosetta_filepath = os.path.join(cdm_data_dir, 'Collection_Fields.json')
    with open(rosetta_filepath, 'r') as f:
        parsed_rosetta_file = json.loads(f.read())
    return {field['nick']: field['name'] for field in parsed_rosetta_file}


def convert_nicks_to_propers(nicks_to_names_dict, nicks_texts):
    propers_texts = dict()
    for k, v in nicks_texts.items():
        if k in nicks_to_names_dict:
            propers_texts[nicks_to_names_dict[k]] = v
    return propers_texts


def subject_split(my_etree):
    pass


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


class ConvertIntoMods():
    def __init__(self, alias):
        self.alias = alias
        cdm_data_dir = os.path.realpath(os.path.join('..', 'revising_cdm_xporter', 'Cached_Cdm_files', self.alias))
        nicks_to_names_dict = make_nicks_to_names(cdm_data_dir)
        self.mappings_dict = parse_mappings_file(self.alias)

        cdm_data_filestructure = [(root, dirs, files) for root, dirs, files in os.walk(cdm_data_dir)]
        root_cdm_pointers = parse_root_cdm_pointers(cdm_data_filestructure)
        for pointer in root_cdm_pointers:
            print(pointer)
            target_file = '{}.json'.format(pointer)
            path_to_pointer = [os.path.join(root, target_file)
                               for root, dirs, files in cdm_data_filestructure
                               if target_file in files][0]

            pointer_json = get_cdm_pointer_json(path_to_pointer)
            nicks_texts = parse_cdm_pointer_json(pointer_json)
            propers_texts = convert_nicks_to_propers(nicks_to_names_dict, nicks_texts)
            self.make_pointer_mods(path_to_pointer, pointer, pointer_json, propers_texts)

    def make_pointer_mods(self, path_to_pointer, pointer, pointer_json, propers_texts):
        NSMAP = {None: "http://www.loc.gov/mods/v3",
                 'mods': "http://www.loc.gov/mods/v3",
                 'xsi': "http://www.w3.org/2001/XMLSchema-instance",
                 'xlink': "http://www.w3.org/1999/xlink", }
        root_element = ET.Element("mods", nsmap=NSMAP)

        for k, v in self.mappings_dict.items():
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
                    self.make_contentDM_elem(new_element[0], pointer, pointer_json)
                root_element.append(new_element)

        subject_split(root_element)

        id_elem = ET.Element("identifier", attrib={'type': 'uri', 'invalid': 'yes', 'displayLabel': "Migrated From"})
        id_elem.text = 'http://cdm16313.contentdm.oclc.org/cdm/singleitem/collection/{}/id/{}'.format(self.alias, pointer)
        root_element.append(id_elem)
        root_element = merge_same_fields(root_element)
        root_element = delete_empty_fields(root_element)

        with open('/home/james/Desktop/trash.xml', 'w') as f:
            f.write(ET.tostring(root_element, pretty_print=True).decode('utf-8'))

    def make_contentDM_elem(self, cdm_elem, pointer, pointer_json):
        alias_elem = ET.Element('alias')
        alias_elem.text = self.alias
        cdm_elem.append(alias_elem)
        pointer_elem = ET.Element('pointer')
        pointer_elem.text = pointer
        cdm_elem.append(pointer_elem)
        dmGetItemInfo_elem = ET.Element('dmGetItemInfo', attrib={
            'mimetype': "application/json",
            'source': "https://server16313.contentdm.oclc.org/dmwebservices/index.php?q=dmGetItemInfo/{}/{}/json".format(self.alias, pointer),
            'timestamp': '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()), })
        dmGetItemInfo_elem.text = pointer_json
        cdm_elem.append(dmGetItemInfo_elem)


if __name__ == '__main__':
    alias = sys.argv[1]
    ConvertIntoMods(alias)
