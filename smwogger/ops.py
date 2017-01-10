import requests
from six.moves.urllib.parse import urlunparse
from smwogger import logger


_OPS = {}


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


def operation(func):
    _OPS[func.__name__] = func

    def _operation(*args, **kw):
        return func(*args, **kw)

    return _operation


class OperationRunner(object):
    def __init__(self, parser, data_picker, verbose=False):
        self.data_picker = data_picker
        self.verbose = verbose
        self.parser = parser
        self.host = parser.specification['host']
        schemes = parser.specification.get('schemes', ['https'])
        self.scheme = schemes[0]
        self.paths = parser.specification['paths']
        self.session = requests.Session()

    def scenario(self):
        scenario = self.data_picker.scenario()
        if scenario == []:
            for opid, options in self.operations():
                yield opid, options
        else:
            ops = dict(list(self.operations()))
            for step in scenario:
                opid, options = step.popitem()
                options.update(ops[opid])
                yield opid, options

    def operations(self):
        for path, spec in self.parser.specification['paths'].items():
            endpoint = urlunparse((self.scheme, self.host, path, '', '', ''))
            for verb, options in spec.items():
                verb = verb.upper()
                options['verb'] = verb.upper()
                options['endpoint'] = endpoint
                yield options['operationId'], options

    def __call__(self, operation_id, **options):
        extra = options.get('request', {}).get('path', {})
        options['endpoint'] = self.data_picker.path(options['endpoint'],
                                                    **extra)
        runner = _OPS.get(operation_id, self._default_runner)
        return runner(operation_id, **options)

    def _default_runner(self, operation_id, **options):
        endpoint = options['endpoint']
        verb = options['verb']

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
        if vars != []:
            for varname, data in vars.items():
                default = data['default']
                query = data['query']
                value = res.json().get(query, default)

            self.data_picker.set_var(varname, value)
