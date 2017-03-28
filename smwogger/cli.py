import sys
from contextlib import contextmanager


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def stdout(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def eol():
    stdout('\n')


@contextmanager
def console(description, success='OK', fail='FAIL', verbose=1):
    if verbose > 0:
        stdout(description + '... ')
    try:
        yield
        if verbose > 0:
            stdout(bcolors.OKGREEN + success + bcolors.ENDC)
    except Exception:
        if verbose > 0:
            stdout(bcolors.FAIL + fail + bcolors.ENDC)
        raise
    if verbose == 0:
        stdout('.')
    else:
        eol()
