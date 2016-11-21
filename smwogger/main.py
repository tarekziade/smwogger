import os
import sys
import argparse

import yaml
import requests
from swagger_parser import SwaggerParser

from smwogger.cli import console
from smwogger.datapicker import DataPicker
from smwogger.ops import OperationRunner


def main():
    parser = argparse.ArgumentParser(
        description='Smwogger. Smoke Tester.')

    parser.add_argument('url', help='Swagger URL')
    args = parser.parse_args()
    url = args.url

    with console("Scanning spec"):
        if os.path.exists(url):
            with open(url) as f:
                swagger = yaml.load(f.read())
        else:
            swagger = yaml.load(requests.get(url).content)

        parser = SwaggerParser(swagger_dict=swagger)
        data = DataPicker(parser.specification['x-smoke-test'])

    print()
    print("\t\tThis is project %r" % parser.specification['info']['title'])
    print("\t\t%s" % parser.specification['info']['description'])
    print("\t\tVersion %s" % parser.specification['info']['version'])
    print()
    print()

    runner = OperationRunner(parser, data)

    for oid, options in runner.scenario():
        with console('Checking %s' % oid):
            try:
                runner(oid, **options)
            except Exception:
                raise
