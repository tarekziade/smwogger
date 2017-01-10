import requests
from functools import partial
from six.moves.urllib.parse import urlunparse
from swagger_parser import SwaggerParser

from smwogger.util import get_content
from smwogger import logger


def print_request(req):
    raw = '\n' + req.method + ' ' + req.url
    if len(req.headers) > 0:
        headers = '\n'.join('%s: %s' % (k, v) for k, v in req.headers.items())
        raw += '\n' + headers

    if req.body:
        raw += '\n\n' + req.body + '\n'

    logger.info(raw)


def print_response(resp):
    raw = 'HTTP/1.1 %s %s\n' % (resp.status_code, resp.reason)
    items = resp.headers.items()
    headers = '\n'.join('{}: {}'.format(k, v) for k, v in items)
    raw += headers

    if resp.content:
        raw += '\n\n' + resp.content.decode()

    logger.info(raw)


class API(object):

    def __init__(self, path_or_url, verbose=False):
        self._content = get_content(path_or_url)
        self._parser = SwaggerParser(swagger_dict=self._content)
        self.spec = self._parser.specification
        self.session = requests.Session()
        self.verbose = verbose
        self.host = self.spec['host']
        schemes = self.spec.get('schemes', ['https'])
        self.scheme = schemes[0]
        self._operations = self._get_operations()

    def __getattr__(self, name):
        if name in self._operations:
            return partial(self._caller, name)
        raise AttributeError(name)

    def _caller(self, operation_id, **options):
        op = self._operations[operation_id]
        data_reader = options.pop('data_reader', None)

        if 'endpoint' in options:
            transformer = options.pop('endpoint')
            op['endpoint'] = transformer(op['endpoint'])
        endpoint = op['endpoint']
        verb = op['verb']
        options.update(op)
        resp_options = options.get('response', {})
        req_options = options.get('request', {})
        extra = {}
        if 'body' in req_options and 'data' not in req_options:
            extra['data'] = req_options.pop('body')

        req = requests.Request(verb, endpoint, **extra)
        prepared = req.prepare()

        if self.verbose:
            print_request(prepared)
            logger.info('>>>')

        res = self.session.send(prepared)

        if self.verbose:
            print_response(res)
            logger.info('<<<')

        # provided by the scenario (maybe should put it in responses)
        if 'status' in resp_options:
            wanted = int(resp_options['status'])
            if res.status_code != wanted:
                print("Bad Status code on %r" % options['endpoint'])
                print("Wanted %d, Got %d" % (wanted, res.status_code))
                raise AssertionError()

        if 'headers' in resp_options:
            for name, expected in resp_options['headers'].items():
                got = res.headers.get(name)
                if got != expected:
                    print('Bad value for header %s' % name)
                    print('Got %r, expected %r' % (got, expected))
                    raise AssertionError()

        # provided by swagger
        else:
            statuses = [int(st) for st in options['responses'].keys()]
            if res.status_code not in statuses:
                print("Bad Status code on %r" % options['endpoint'])
                statuses = ' or '.join(['%d' for s in statuses])
                print("Wanted %s, Got %d" % (statuses, res.status_code))
                raise AssertionError()

        # extracting variables if needed
        vars = resp_options.get('vars', [])
        if vars != [] and data_reader:
            json_data = res.json()
            for varname, data in vars.items():
                default = data['default']
                query = data['query']
                value = json_data.get(query, default)
                data_reader(varname, value)

    def _get_operations(self):
        ops = {}
        for path, spec in self.spec['paths'].items():
            endpoint = urlunparse((self.scheme, self.host, path, '', '', ''))
            for verb, options in spec.items():
                verb = verb.upper()
                options['verb'] = verb.upper()
                options['endpoint'] = endpoint
                ops[options['operationId']] = options
        return ops
