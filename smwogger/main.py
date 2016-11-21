import os
import argparse
import logging

import yaml
import requests
from swagger_parser import SwaggerParser

from smwogger import logger
from smwogger.cli import console
from smwogger.datapicker import DataPicker
from smwogger.ops import OperationRunner


def get_runner(url, verbose=False):
    if os.path.exists(url):
        with open(url) as f:
            swagger = yaml.load(f.read())
    else:
        swagger = yaml.load(requests.get(url).content)

    parser = SwaggerParser(swagger_dict=swagger)
    data = DataPicker(parser.specification['x-smoke-test'])
    return OperationRunner(parser, data, verbose=verbose)


def main():
    parser = argparse.ArgumentParser(
        description='Smwogger. Smoke Tester.')

    parser.add_argument('url', help='Swagger URL')
    parser.add_argument('-v', '--verbose', help="Display more info",
                        action='store_true', default=False)

    args = parser.parse_args()
    url = args.url

    if args.verbose:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False

    with console("Scanning spec"):
        runner = get_runner(url, verbose=args.verbose)

    print()
    print("\t\tThis is project %r" % parser.specification['info']['title'])
    print("\t\t%s" % parser.specification['info']['description'])
    print("\t\tVersion %s" % parser.specification['info']['version'])
    print()
    print()

    print('Running Scenario')
    for index, (oid, options) in enumerate(runner.scenario()):
        with console('%d:%s' % (index + 1, oid)):
            try:
                runner(oid, **options)
            except Exception:
                raise
