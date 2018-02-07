#!/usr/bin/env python2
# pylint: disable=missing-docstring,invalid-name,import-error
"""Create IGV session for BCM."""
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
from lxml import etree
import os

parser = argparse.ArgumentParser(description="Create igv session")

parser.add_argument('-n', '--dataset_name', required=True, help="Name of dataset/collection.")
parser.add_argument('-g', '--genome', help="Geneome and annotation hosted by IGV.")
parser.add_argument('-b', '--bam_files', required=False, nargs='*', help="List of bam files.")
parser.add_argument('-f', '--all_files', required=False, nargs='*', help="List of files.")

args = parser.parse_args()

args = parser.parse_args()
xml_name = str(args.dataset_name) + '.xml'
base_url = 'http://taco-wiki.grid.bcm.edu/genialis/igv/'
session_url = base_url + xml_name

registry_path = '/web/igv/registry.txt'


if not os.path.isfile(registry_path):
    with open(registry_path, 'w') as f:
        f.write('{}\n'.format(session_url))
else:
    with open(registry_path, "r+") as f:
        line_found = any(xml_name in line for line in f)
        if line_found:
            msg = "This name of xml file already exsist, please select different dataset name."
            print(msg)
            raise ValueError(msg)
        else:
            f.seek(0, os.SEEK_END)
            f.write("{}\n".format(session_url))


Global = etree.Element(
    'Global',
    name=args.dataset_name,
    genome=args.genome,
    version='3'
)

general_path = '/storage/genialis/bcm.genialis.com'

for bam in args.bam_files or []:
    bam_id = os.path.basename(os.path.dirname(bam))
    bam_name = os.path.basename(bam)
    bam_path = os.path.join('..', '..', '..', 'bcm.genialis.com', 'data', bam_id, bam_name)

    docker_path = os.path.join('/web', 'igv', bam_id)

    if not os.path.isdir(docker_path):
        current_dir = os.getcwd()
        os.chdir('/web/igv')
        os.mkdir('/web/igv/{}'.format(bam_id))
        os.popen('ln -s {} {}'.format(bam_path, docker_path))
        os.popen('ln -s {}.bai {}'.format(bam_path, docker_path))
        os.chdir(current_dir)

    resource_link = base_url + bam_id + '/' + bam_name
    Resource = etree.SubElement(Global, 'Resource', name=bam_name, path=resource_link)

for element in args.all_files or []:
    element_id = os.path.basename(os.path.dirname(element))
    element_name = os.path.basename(element)
    element_path = os.path.join('..', '..', '..', 'bcm.genialis.com', 'data', element_id, element_name)

    docker_path = os.path.join('/web', 'igv', element_id)

    if not os.path.isdir(docker_path):
        current_dir = os.getcwd()
        os.chdir('/web/igv')
        os.mkdir('/web/igv/{}'.format(element_id))
        os.popen('ln -s {} {}'.format(element_path, docker_path))
        os.chdir(current_dir)
    else:
        file_path = os.path.join('/web', 'igv', element_id, element_name)
        if not os.path.isfile(file_path):
            current_dir = os.getcwd()
            os.popen('ln -s {} {}'.format(element_path, file_path))
            os.chdir(current_dir)

    e_resource_link = base_url + element_id + '/' + element_name
    Resource = etree.SubElement(Global, 'Resource', name=element_name, path=e_resource_link)


doc = etree.tostring(Global, pretty_print=True, xml_declaration=True, encoding='UTF-8')

with open('/web/igv/' + xml_name, 'w') as f:
    f.write(doc)
