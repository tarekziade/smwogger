import requests

_OPS = {}


def default_op(verb, endpoint, **options):
    if verb != 'GET':
        raise NotImplementedError()

    res = requests.get(endpoint)
    statuses = [int(st) for st in options['responses'].keys()]
    assert res.status_code in statuses


def get_operation(name):
    return _OPS.get(name, default_op)


def operation(func):
    _OPS[func.__name__] = func

    def _operation(*args, **kw):
        return func(*args, **kw)

    return _operation
