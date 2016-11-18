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

    def scenario(self):
        scenario = self.data_picker.scenario()
        if scenario == []:
            return self.operations()
        else:
            ops = dict(list(self.operations()))
            for opid, options in scenario:
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
        options['endpoint'] = self.data_picker.path(options['endpoint'])
        runner = _OPS.get(operation_id, self._default_runner)
        return runner(operation_id, **options)

    def _default_runner(self, operation_id, **options):
        meth = getattr(requests, options['verb'].lower())
        res = meth(options['endpoint'])
        # provided by the scenario (maybe should put it in responses)
        if 'status' in options:
            if res.status_code != int(options['status']):
                print("Bad Status code on %r" % options['endpoint'])
                print("Wanted %d, Got %d" % (int(options['status']),
                                             res.status_code))
                raise AssertionError()

        # provided by swagger
        else:
            statuses = [int(st) for st in options['responses'].keys()]
            if res.status_code not in statuses:
                print("Bad Status code on %r" % options['endpoint'])
                print("Wanted %s, Got %d" % (' or '.join(['%d' for s in statuses]),
                                             res.status_code))
                raise AssertionError()

        # extracting variables if needed
        vars = options.get('vars', [])
        if vars != []:
            for varname, data in vars.items():
                default = data['default']
                query = data['query']
                value = res.json().get(query, default)

            self.data_picker.set_var(varname, value)

    def get_operation(name):
        return _OPS.get(name, default_op)
