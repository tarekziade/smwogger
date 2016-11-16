import requests
from six.moves.urllib.parse import urlunparse


_OPS = {}


def operation(func):
    _OPS[func.__name__] = func

    def _operation(*args, **kw):
        return func(*args, **kw)

    return _operation


class OperationRunner(object):
    def __init__(self, parser, data_picker):
        self.data_picker = data_picker
        self.parser = parser
        self.host = parser.specification['host']
        schemes = parser.specification.get('schemes', ['https'])
        self.scheme = schemes[0]
        self.paths = parser.specification['paths']

    def items(self):
        for path, spec in self.parser.specification['paths'].items():
            endpoint = urlunparse((self.scheme, self.host, path, '', '', ''))
            for verb, options in spec.items():
                verb = verb.upper()
                yield verb, endpoint, options

    def __call__(self, verb, endpoint, **options):
        endpoint = self.data_picker.path(endpoint)
        oid = options['operationId']
        runner = _OPS.get(oid, self._default_runner)
        return runner(verb, endpoint, **options)

    def _default_runner(self, verb, endpoint, **options):
        meth = getattr(requests, verb.lower())
        res = meth(endpoint)
        statuses = [int(st) for st in options['responses'].keys()]
        assert res.status_code in statuses

    def get_operation(name):
        return _OPS.get(name, default_op)
