import unittest
import os

from smwogger.api import API
from smwogger.tests.support import coserver, async_test


HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, 'absearch.yaml')


class TestAPI(unittest.TestCase):

    @async_test
    async def test_names(self, loop):
        async with API(SPEC, verbose=True, loop=loop) as api:
            with coserver():
                await api.getHeartbeat()

            for attr in ('getHeartbeat', 'addUserToCohort',
                         'returnCohortSettings'):
                self.assertTrue(hasattr(api, attr))

    @async_test
    async def test_default(self, loop):
        async with API(SPEC, loop=loop) as api:
            with coserver():
                await api.getDefault()

    @async_test
    async def test_read_spec_from_url(self, loop):
        headers = {'Something': 'here'}

        with coserver():
            async with API('http://localhost:8888/api.yaml', verbose=True,
                           loop=loop) as api:
                await api.getDefault()

            async with API('http://localhost:8888/api.json', verbose=True,
                           loop=loop) as api:
                await api.getDefault()
                res = await api.getHeartbeat(request={'headers': headers})

        data = await res.json()
        echoed_headers = data['headers']
        self.assertEqual(echoed_headers['Something'], 'here')

    @async_test
    async def test_bad_method(self, loop):
        async with API(SPEC, verbose=True, loop=loop) as api:
            try:
                await api.iDontExist()
                raise AssertionError("WAT")
            except AttributeError:
                pass

    @async_test
    async def test_bad_status(self, loop):
        with coserver():
            async with API('http://localhost:8888/api.yaml', verbose=True,
                           loop=loop) as api:
                try:
                    await api.getBadStatus()
                    raise AssertionError("WAT")
                except AssertionError:
                    pass
