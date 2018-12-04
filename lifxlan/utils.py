import time
from collections import deque
from concurrent.futures import wait
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from functools import wraps
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, socket, timeout
from typing import Optional, List, Generator, Any, Union
from .errors import WorkflowException


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            print(f'func {func.__name__!r} took {time.time() - start_time} seconds')

    return wrapper


@contextmanager
def localtimer():
    start_time = time.time()
    try:
        yield
    finally:
        print(f'localtimer took {time.time() - start_time}')


class WaitPool:
    """
    allow jobs to be submitted to either an existing pool or a dynamically-created one,
    wait for it to complete, and have access to the futures outside the `with` block
    """
    threads_per_pool = 8

    def __init__(self, pool: Optional[Union[int, ThreadPoolExecutor]] = None):
        self._pool = self._init_pool(pool)
        self._futures = []

    @staticmethod
    def _init_pool(pool: Optional[Union[int, ThreadPoolExecutor]]):
        if isinstance(pool, ThreadPoolExecutor):
            return pool

        if isinstance(pool, int):
            num_threads = pool
        elif pool is None:
            num_threads = WaitPool.threads_per_pool
        else:
            raise ValueError(f'invalid value for `pool`: {pool!r}')

        return ThreadPoolExecutor(num_threads)

    @property
    def futures(self):
        return self._futures

    @property
    def results(self) -> List[Any]:
        return [f.result() for f in self._futures]

    def wait(self):
        wait(self.futures)

    def __getattr__(self, item):
        """proxy for underlying pool object"""
        return getattr(self._pool, item)

    def submit(self, fn, *args, **kwargs):
        fut = self._pool.submit(fn, *args, **kwargs)
        self._futures.append(fut)
        return fut

    def map(self, fn, *iterables):
        self._futures.extend(self._pool.submit(fn, *args) for args in zip(*iterables))

    def dispatch(self, fn, *args, **kwargs):
        """run on thread pool but don't wait for completion"""
        return self._pool.submit(fn, *args, **kwargs)

    def __enter__(self):
        self._futures.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()


def exhaust(iterable):
    """
    immediately consume an iterable and discard results

    should be used for side effects (printing, updating, submitting to job pool, etc)
    """
    deque(iterable, maxlen=0)


@contextmanager
def init_socket(timeout):
    sock = socket(AF_INET, SOCK_DGRAM)
    try:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.settimeout(timeout)
        try:
            sock.bind(("", 0))  # allow OS to assign next available source port
        except Exception as err:
            raise WorkflowException("WorkflowException: error {} while trying to open socket".format(str(err)))
        yield sock
    finally:
        sock.close()
