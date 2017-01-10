import argparse
import logging
from functools import partial
import imp

from smwogger import logger
from smwogger.cli import console
from smwogger.api import API
from smwogger.smoketest import SmokeTest


def get_runner(url, test_url=None, verbose=False):
    if test_url and test_url.endswith('.py'):
        script = imp.load_source('script', test_url)
        return partial(script.scenario, API(url, verbose=verbose))
    else:
        return SmokeTest(API(url, verbose=verbose), test_url)


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

    if isinstance(runner, SmokeTest):
        spec = runner.api.spec
        print()
        print("\t\tThis is project %r" % spec['info']['title'])
        print("\t\t%s" % spec['info']['description'])
        print("\t\tVersion %s" % spec['info']['version'])
        print()
        print()

        print('Running Scenario from x-smoke-test')
        for index, (oid, options) in enumerate(runner.scenario()):
            with console('%d:%s' % (index + 1, oid)):
                try:
                    runner(oid, **options)
                except Exception:
                    raise
    else:
        print('Running Python Scenario')
        runner()
