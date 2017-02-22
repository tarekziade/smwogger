import unittest
import os

from smwogger.api import API
from smwogger.tests.support import coserver


HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, 'absearch.yaml')


class TestAPI(unittest.TestCase):

    def test_names(self):
        api = API(SPEC)

        with coserver():
            api.getHeartbeat()

        for attr in ('getHeartbeat', 'addUserToCohort',
                     'returnCohortSettings'):
            self.assertTrue(hasattr(api, attr))

    def test_default(self):
        api = API(SPEC)

        with coserver():
            api.getDefault()
