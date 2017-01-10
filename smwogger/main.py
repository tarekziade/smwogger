import os
import argparse
import logging
import mimetypes

import yaml
import requests
from swagger_parser import SwaggerParser

from smwogger import logger
from smwogger.cli import console
from smwogger.datapicker import DataPicker
from smwogger.ops import OperationRunner


_JSON_TYPES = ('application/vnd.api+json', 'application/json')
_YAML_TYPES = ('application/x-yaml', 'text/yaml')

if '.yaml' not in mimetypes.types_map:
    mimetypes.types_map['.yaml'] = 'application/x-yaml'


def _decoder(mime):
    if mime in _YAML_TYPES:
        return yaml.load
    # we'll just try json
    return yaml.load


def get_content(url):
    if os.path.exists(url):
        mime = mimetypes.guess_type(url)[0]
        with open(url) as f:
            return _decoder(mime)(f.read())
    else:
        resp = requests.get(url)
        content_type = resp.header.get('Content-Type', 'application/json')
        return _decoder(content_type)(requests.get(url).content)


def get_runner(url, test_url=None, verbose=False):
    swagger = get_content(url)
    parser = SwaggerParser(swagger_dict=swagger)
    spec = parser.specification

    if test_url is not None:
        spec['x-smoke-test'] = get_content(test_url)['x-smoke-test']

    data = DataPicker(spec['x-smoke-test'])
    return OperationRunner(parser, data, verbose=verbose)


def main():
    parser = argparse.ArgumentParser(
        description='Smwogger. Smoke Tester.')

    parser.add_argument('url', help='Swagger URL or file')
    parser.add_argument('--test', help='Test URL or file',
                        default=None)

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
        runner = get_runner(url, test_url=args.test, verbose=args.verbose)

    spec = runner.parser.specification

    print()
    print("\t\tThis is project %r" % spec['info']['title'])
    print("\t\t%s" % spec['info']['description'])
    print("\t\tVersion %s" % spec['info']['version'])
    print()
    print()

    print('Running Scenario')
    for index, (oid, options) in enumerate(runner.scenario()):
        with console('%d:%s' % (index + 1, oid)):
            try:
                runner(oid, **options)
            except Exception:
                raise
