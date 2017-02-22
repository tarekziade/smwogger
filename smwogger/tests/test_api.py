import unittest
import os

from smwogger.api import API
from smwogger.tests.support import coserver


HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, 'absearch.yaml')


class TestAPI(unittest.TestCase):

    def test_names(self):
        api = API(SPEC, verbose=True)

        with coserver():
            api.getHeartbeat()

        for attr in ('getHeartbeat', 'addUserToCohort',
                     'returnCohortSettings'):
            self.assertTrue(hasattr(api, attr))

    def test_default(self):
        api = API(SPEC)

        with coserver():
            api.getDefault()

    def test_read_spec_from_url(self):
        headers = {'Something': 'here'}

        with coserver():
            api = API('http://localhost:8888/api.yaml', verbose=True)
            api.getDefault()

            api = API('http://localhost:8888/api.json', verbose=True)
            api.getDefault()

            res = api.getHeartbeat(request={'headers': headers})

        echoed_headers = res.json()['headers']
        self.assertEqual(echoed_headers['Something'], 'here')

    def test_bad_method(self):
        api = API(SPEC, verbose=True)
        try:
            api.iDontExist()
            raise AssertionError("WAT")
        except AttributeError:
            pass

    def test_bad_status(self):
        with coserver():
            api = API('http://localhost:8888/api.yaml', verbose=True)
            self.assertRaises(AssertionError, api.getBadStatus)
