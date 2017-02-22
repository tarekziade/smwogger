import sys
import signal
import os
import multiprocessing
import time
from contextlib import contextmanager
from http.client import HTTPConnection
from io import StringIO


def run_server(port=8888):
    """Running in a subprocess to avoid any interference
    """
    def _run():
        from smwogger.tests.service import application
        import signal
        import sys

        def _shutdown(*args, **kw):
            application.close()
            sys.exit(0)

        signal.signal(signal.SIGTERM, _shutdown)
        signal.signal(signal.SIGINT, _shutdown)
        application.run(host='localhost', port=port)

    p = multiprocessing.Process(target=_run)
    p.start()
    start = time.time()
    connected = False

    while time.time() - start < 5 and not connected:
        try:
            conn = HTTPConnection('localhost', port)
            conn.request("GET", "/")
            conn.getresponse()
            connected = True
        except Exception:
            time.sleep(.1)
    if not connected:
        os.kill(p.pid, signal.SIGTERM)
        p.join(timeout=1.)
        raise OSError('Could not connect to coserver')
    return p


_CO = {'clients': 0, 'server': None}


@contextmanager
def coserver(port=8888):
    if _CO['clients'] == 0:
        _CO['server'] = run_server(port)

    _CO['clients'] += 1
    try:
        yield
    finally:
        _CO['clients'] -= 1
        if _CO['clients'] == 0:
            os.kill(_CO['server'].pid, signal.SIGTERM)
            _CO['server'].join(timeout=1.)
            _CO['server'] = None


@contextmanager
def set_args(*args):
    old = list(sys.argv)
    sys.argv[:] = args
    oldout, olderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = StringIO(), StringIO()
    try:
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout.seek(0)
        sys.stderr.seek(0)
        sys.argv[:] = old
        sys.stdout, sys.stderr = oldout, olderr
