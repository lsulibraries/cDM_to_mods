#! /usr/bin/env python3

import os
from lxml import etree as ET


class MonographTitleCombiner:
    def __init__(self, alias_data_dir):
        self.alias_data_dir = alias_data_dir
        self.monograph_pointer_newtitle = dict()
        self.main()

    def main(self):
        structure_files = [os.path.join(root, file)
                           for root, dirs, files in os.walk(self.alias_data_dir)
                           for file in files
                           if "_cpd.xml" in file]
        for structure_file in sorted(structure_files):
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
        # elem_nodetitle = self.get_this_level_nodetitle(elem)
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
            raise Exception('Error:  a page and node on the same level')

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
                new_title = '{} {}'.format(elem_nodetitle, title)
            else:
                new_title = title
            self.monograph_pointer_newtitle[pointer] = new_title

    def get_this_level_nodetitle(self, elem):
        nodetitle_elem = elem.find('nodetitle')
        if nodetitle_elem is not None:
            return nodetitle_elem.text
        raise Exception('No nodetitle at this level {}'.format(elem.tag))

    def children_meet_expectations(self, elem, expected_elems=[], silent_elems=[], unique_elems=[]):
        unique_set = set()
        for child in elem.iterchildren():
            if child.tag not in expected_elems:
                raise Exception('Unexpected node tag {}'.format(child.tag))
            if child.tag in silent_elems and self.has_text(child):
                raise Exception('Not capturing data in {}'.format(child.tag, child.text))
            if child.tag in unique_elems and child.tag in unique_set:
                raise Exception('Duplicate tag {}'.format(child.tag))
            else:
                unique_set.add(child.tag)
        return True

    @staticmethod
    def has_text(elem):
        return elem.text and isinstance(elem.text, str) and len(elem.text.strip()) > 0
