import unittest
import os
from smwogger.api import API


HERE = os.path.dirname(__file__)
SPEC = os.path.join(HERE, 'absearch.yaml')


class TestAPI(unittest.TestCase):

    def test_names(self):
        api = API(SPEC)

        api.getHeartbeat()

        for attr in ('getHeartbeat', 'addUserToCohort',
                     'returnCohortSettings'):
            self.assertTrue(hasattr(api, attr))
