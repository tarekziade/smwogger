import sys
from contextlib import contextmanager

import yaml
import requests
from six.moves.urllib.parse import urlunparse
from swagger_parser import SwaggerParser

from smwogger.ops import get_operation


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def stdout(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def eol():
    stdout('\n')


@contextmanager
def console(description, success='OK', fail='FAIL'):
    stdout(description + '... ')
    try:
        yield
        stdout(bcolors.OKGREEN + success + bcolors.ENDC)
    except Exception:
        stdout(bcolors.FAIL + fail + bcolors.ENDC)
        raise
    eol()



def main():
    with console("Scanning spec"):
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

            with console('Checking %s %s' % (verb, endpoint)):
                try:
                    func(verb, endpoint, **options)
                except Exception:
                    raise
