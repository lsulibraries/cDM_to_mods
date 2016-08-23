#! /usr/bin/python3

import os
import configparser


def pull_xlsts(file):
    with open(file, 'r') as f:
        file_text = f.readlines()
    return [line.split('=')[-1].strip().split('/')[-1].replace('.xsl\'', '') for line in file_text if 'stylesheets[]' in line]

source_dir = '/home/james/Desktop/lsu_git/mik/extras/lsu/configuration_files/'
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

alias_list = {file.replace('_simple.ini', '').replace('_compound.ini', '') for file in os.listdir(source_dir)}

for alias in alias_list:
    simple_ini = os.path.realpath(os.path.join(source_dir, '{}_simple.ini'.format(alias)))
    compound_ini = os.path.realpath(os.path.join(source_dir, '{}_compound.ini'.format(alias)))

    if not os.path.isfile(simple_ini):
        print(alias, 'no simple')
    if not os.path.isfile(compound_ini):
        print(alias, 'no compound')

    simple_text = '\n'.join(pull_xlsts(simple_ini))
    compounds_text = '\n'.join(pull_xlsts(compound_ini))
    if simple_text != compounds_text:
        print('whoa')
    else:
        with open('output/{}.txt'.format(alias) , 'w') as f:
            f.write(simple_text)
