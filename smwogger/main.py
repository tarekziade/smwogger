import argparse
import logging
from functools import partial
import imp
import asyncio

from smwogger import logger
from smwogger.cli import console
from smwogger.api import API
from smwogger.smoketest import SmokeTest


def get_runner(api, url, test_url=None, verbose=0, stream=None):
    if test_url and test_url.endswith('.py'):
        script = imp.load_source('script', test_url)
        return partial(script.scenario, api)
    else:
        return SmokeTest(api, test_url)


DONE = object()


async def log(queue):
    while True:
        try:
            item = queue.get_nowait()
        except RuntimeError:
            break
        except asyncio.QueueEmpty:
            await asyncio.sleep(.2)
        else:
            if item == DONE:
                return
            else:
                logger.info(item)


def main():
    parser = argparse.ArgumentParser(
        description='Smwogger. Smoke Tester.')

    parser.add_argument('url', help='Swagger URL or file')
    parser.add_argument('--test', help='Test URL or file',
                        default=None)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help=('Verbosity level. -v will display '
                              'tracebacks. -vv requests and responses.'))

    args = parser.parse_args()
    url = args.url

    if args.verbose > 0:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False

    loop = asyncio.get_event_loop()
    stream = asyncio.Queue()
    api = API(url, verbose=args.verbose, stream=stream)

    try:
        with console("Scanning spec"):
            runner = get_runner(api, url, test_url=args.test,
                                verbose=args.verbose,
                                stream=stream)

        coros = []
        if isinstance(runner, SmokeTest):
            spec = runner.api.spec
            print()
            print("\t\tThis is project %r" % spec['info']['title'])
            print("\t\t%s" % spec['info']['description'])
            print("\t\tVersion %s" % spec['info']['version'])
            print()
            print()

            print('Running Scenario from x-smoke-test')

            async def _scenario():
                for index, (oid, options) in enumerate(runner.scenario()):
                    with console('%d:%s' % (index + 1, oid)):
                        try:
                            await runner(oid, **options)
                        except Exception:
                            raise
                await stream.put(DONE)

            coros.append(_scenario())
        else:
            print('Running Python Scenario')

            async def single_run():
                await runner()
                await stream.put(DONE)

            coros.append(single_run())

        coros.append(log(stream))
        loop.run_until_complete(asyncio.gather(*coros))
    finally:
        api.close()
        loop.close()
