import sys

import yaml
import requests
from six.moves.urllib.parse import urlunparse
from swagger_parser import SwaggerParser

from smwogger.ops import get_operation


def main():
    url = sys.argv[1]
    swagger = yaml.load(requests.get(url).content)

    parser = SwaggerParser(swagger_dict=swagger)
    host = parser.specification['host']
    schemes = parser.specification.get('schemes', ['https'])
    scheme = schemes[0]

    for path, spec in parser.specification['paths'].items():
        for verb, options in spec.items():
            operation = options['operationId']
            func = get_operation(operation)
            endpoint = urlunparse((scheme, host, path, '', '', ''))
            verb = verb.upper()
            print('Checking %s %s...' % (verb, endpoint))
            try:
                func(verb, endpoint, **options)
                print('OK')
            except Exception:
                print('FAIL')
                raise
