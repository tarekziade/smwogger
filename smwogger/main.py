import sys
import argparse

import yaml
import requests
from six.moves.urllib.parse import urlunparse
from swagger_parser import SwaggerParser

from smwogger.ops import get_operation
from smwogger.cli import console


def main():
    parser = argparse.ArgumentParser(
        description='Smwogger. Smoke Tester.')

    parser.add_argument('--data', help='Data file or URL',
                        type=str, default=None)

    parser.add_argument('url', help='Swagger URL')
    args = parser.parse_args()
    url = args.url

    with console("Scanning spec"):
        swagger = yaml.load(requests.get(url).content)
        parser = SwaggerParser(swagger_dict=swagger)
        host = parser.specification['host']
        schemes = parser.specification.get('schemes', ['https'])
        scheme = schemes[0]

    print()
    print("\t\tThis is project %r" % parser.specification['info']['title'])
    print("\t\t%s" % parser.specification['info']['description'])
    print("\t\tVersion %s" % parser.specification['info']['version'])
    print()
    print()

    for path, spec in parser.specification['paths'].items():
        for verb, options in spec.items():
            operation = options['operationId']
            func = get_operation(operation)
            endpoint = urlunparse((scheme, host, path, '', '', ''))
            verb = verb.upper()

            with console('Checking %s %s' % (verb, endpoint)):
                try:
                    func(verb, endpoint, **options)
                except Exception:
                    raise
