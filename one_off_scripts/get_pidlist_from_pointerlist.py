#! usr/bin/env python3

import urllib.request
import os
from lxml import etree as ET

# namepids is a list of all items in your collection -- get this from sparql
# restricted_pointers is your list of pointers you want restricted


NAMESPACE = "uno-p16313coll22"
NAMEPIDS = ['namespace:pid', 'namespace:pid2']  
RESTRICTED_POINTERS = ['this is your list of pointers from ']


# SPARQL for getting all items in a collection
"""
SELECT ?pid
FROM <#ri>
WHERE {
  {?pid <fedora-rels-ext:isMemberOfCollection> ?parent}
  UNION
  {?pid <fedora-rels-ext:isConstituentOf> ?parent}
  filter regex(str(?parent), "loyno-p120701coll17")
  }
ORDER BY ?pid
"""


def retrieve_binary(namepid):
    url = 'http://ldl.lib.lsu.edu/islandora/object/{}/datastream/MODS/view'.format(namepid)
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')


def write_xml_to_file(xml_text, folder, filename):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, '{}.xml'.format(filename))
    with open(filepath, 'w') as f:
        f.write(xml_text)


output_dir = 'mods_files/{}/'.format(NAMESPACE)
os.makedirs(output_dir, exist_ok=True)
namepid_files = [i for i in os.listdir(output_dir)]

for namepid in NAMEPIDS:
    _, pid = namepid.split(':')
    if '{}.xml'.format(pid) not in namepid_files:
        xml_text = retrieve_binary(namepid)
        write_xml_to_file(xml_text, output_dir, pid)

namepid_files = [os.path.join(root, file)
                 for root, dirs, files in os.walk(output_dir)
                 for file in files
                 if os.path.splitext(file)[1] == '.xml']
pointers_pids = dict()
for xml_file in namepid_files:
    pid = xml_file.split('.')[0].split('/')[-1]
    file_etree = ET.parse(xml_file)
    this_elem_text = [i.text for i in file_etree.getroot() if i.tag == '{http://www.loc.gov/mods/v3}identifier' and i.attrib['displayLabel'] == 'Migrated From'][0]
    pointer = this_elem_text.split('/')[-1]
    pointers_pids[pointer] = pid

# this i


restricted_pids = []
for pointer in RESTRICTED_POINTERS:
    restricted_pids.append("{}:{}".format(NAMESPACE, pointers_pids[pointer]))

print(restricted_pids)
