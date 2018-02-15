from functools import partial
from six.moves.urllib.parse import urlunparse
from swagger_parser import SwaggerParser
from molotov.session import LoggedClientSession
from smwogger.util import get_content


class API(object):
    def __init__(self, path_or_url, verbose=False, loop=None,
                 stream=None):
        self._content = get_content(path_or_url)
        self._parser = SwaggerParser(swagger_dict=self._content)
        self.spec = self._parser.specification
        self.verbose = verbose
        self.host = self.spec['host']
        if 'basePath' in self.spec:
            self.host += self.spec['basePath']
        schemes = self.spec.get('schemes', ['https'])
        self.scheme = schemes[0]
        self.running = True
        self._operations = self._get_operations()
        self.session = LoggedClientSession(loop, stream, verbose=verbose)

    def close(self):
        self.session.close()
        self.running = False

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)
        await self.session.close()
        self.running = False

    def __enter__(self):
        self.session.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.__exit__(exc_type, exc_val, exc_tb)
        self.session.close()
        self.running = False

    def __getattr__(self, name):
        if name == 'operations':
            ops = list(self._get_operations().keys())
            ops.sort()
            return ops

        if name in self._operations:
            return partial(self._caller, name)
        raise AttributeError(name)

    async def _caller(self, operation_id, vars=None, **options):
        op = self._operations[operation_id]
        if vars is None:
            vars = {}

        data_reader = options.pop('data_reader', None)
        endpoint = op['endpoint'].format(**vars)
        verb = op['verb']
        options.update(op)
        resp_options = options.get('response', {})
        req_options = options.get('request', {})

        func = getattr(self.session, verb.lower())
        extra = {}
        extra['data'] = req_options.get('body') or req_options.get('data')
        extra['headers'] = req_options.get('headers')
        extra['params'] = req_options.get('params')

        async with func(endpoint, **extra) as resp:
            return await self._check_response(resp, resp_options, data_reader,
                                              options)

    async def _check_response(self, resp, resp_options, data_reader, options):
        check = options.get('check', True)
        status = resp.status

        # provided by the scenario (maybe should put it in responses)
        if check and 'status' in resp_options:
            wanted = int(resp_options['status'])
            if status != wanted:
                print("Bad Status code on %r" % options['endpoint'])
                print("Wanted %d, Got %d" % (wanted, status))
                body = await resp.text()
                raise AssertionError(body)

        if check and 'headers' in resp_options:
            for name, expected in resp_options['headers'].items():
                got = resp.headers.get(name)
                if got != expected:
                    print('Bad value for header %s' % name)
                    print('Got %r, expected %r' % (got, expected))
                    body = await resp.text()
                    raise AssertionError(body)

        # provided by swagger
        elif check:
            if 'default' not in options['responses']:
                # default means the status can be anything
                # so we're skipping this test
                # Note that in the future if we do more than asserting
                # the status code, we will nee to iterate over the responses
                # options even when default is present
                statuses = [int(st) for st in options['responses'].keys()]
                if status not in statuses:
                    print("Bad Status code on %r" % options['endpoint'])
                    statuses = ' or '.join(['%d' % s for s in statuses])
                    print("Wanted %s, Got %d" % (statuses, status))
                    body = await resp.text()
                    raise AssertionError(body)

        # extracting variables if needed
        vars = resp_options.get('vars')
        if vars and data_reader:
            json_data = await resp.json()

            for varname, data in vars.items():
                default = data.get('default')
                query = data['query']
                value = json_data.get(query, default)
                data_reader(varname, value)

        return resp

    def _get_operations(self):
        ops = {}
        for path, spec in self.spec['paths'].items():
            endpoint = urlunparse((self.scheme, self.host, path, '', '', ''))
            for verb, options in spec.items():
                if verb == 'parameters':
                    continue
                verb = verb.upper()
                options['verb'] = verb.upper()
                options['endpoint'] = endpoint
                ops[options['operationId']] = options
        return ops
