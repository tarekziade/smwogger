import asyncio
import sys
import signal
import os
import multiprocessing
import time
from contextlib import contextmanager
from http.client import HTTPConnection
import functools
from io import StringIO


def run_server(port=8888):
    """Running in a subprocess to avoid any interference
    """
    def _run():
        import sys
        import io

        sys.stderr = sys.stdout = io.StringIO()

        from smwogger.tests.service import application
        import signal

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


def async_test(func):
    @functools.wraps(func)
    def _async_test(*args, **kw):
        cofunc = asyncio.coroutine(func)
        oldloop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(True)
        kw['loop'] = loop
        try:
            loop.run_until_complete(cofunc(*args, **kw))
        finally:
            loop.stop()
            loop.close()
            asyncio.set_event_loop(oldloop)
    return _async_test


def dedicatedloop(func):
    @functools.wraps(func)
    def _loop(*args, **kw):
        old_loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return func(*args, **kw)
        finally:
            asyncio.set_event_loop(old_loop)
    return _loop
