import os
import unittest

from smwogger.tests.support import set_args, coserver
from smwogger.main import main


_SCENARIO = os.path.join(os.path.dirname(__file__), 'scenario.py')
WANTED = """\
Scanning spec... \x1b[92mOK\x1b[0m

\t\tThis is project 'ABSearch Server'
\t\tlightweight a/b testing tool for search options
\t\tVersion 0.3.0


Running Scenario from x-smoke-test
1:getHeartbeat... \x1b[92mOK\x1b[0m
2:addUserToCohort... \x1b[92mOK\x1b[0m
3:returnCohortSettings... \x1b[92mOK\x1b[0m"""


WANTED2 = """\
Scanning spec... \x1b[92mOK\x1b[0m
Running Python Scenario
Getting heartbeat... \x1b[92mOK\x1b[0m
Playing with the cohorts... \x1b[92mOK\x1b[0m"""


class TestMain(unittest.TestCase):

    def test_main(self):

        options = 'smwogger', 'http://localhost:8888/api.json', '--verbose'

        with coserver(), set_args(*options) as out:
            try:
                main()
            except SystemExit:
                pass

        stdout = out[0].read().strip()
        self.assertEqual(stdout, WANTED)
        stderr = out[1].read().strip()
        self.assertTrue("Content-Type: application/json" in stderr)

    def test_scenario(self):
        options = ('smwogger', '--test', _SCENARIO,
                   'http://localhost:8888/api.json')

        with coserver(), set_args(*options) as out:
            try:
                main()
            except SystemExit:
                pass

        stdout = out[0].read().strip()
        self.assertEqual(stdout, WANTED2)
