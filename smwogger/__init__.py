import logging


logger = logging.getLogger('smwogger')    # NOQA
logging.basicConfig(level=logging.WARNING)

try:
    from smwogger.api import API          # NOQA
except ImportError:
    # first import (setuptools)
    pass                                  # NOQA
