import logging
import time
from collections import deque
from concurrent.futures import wait
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import contextmanager
from functools import wraps
from itertools import cycle
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, socket
from threading import local
from typing import Optional, List, Any, Union, Iterable


def init_log(name, level=logging.INFO):
    """create logger using consistent settings"""
    log = logging.getLogger(name)
    log.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


log = init_log(__name__)


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            log.info(f'func {func.__name__!r} took {time.time() - start_time} seconds')

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
        self._local = local()

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
        try:
            f = self._local.futures
        except AttributeError:
            f = self._local.futures = []
        return f

    @property
    def results(self) -> List[Any]:
        return [f.result() for f in self.futures]

    def wait(self):
        wait(self.futures)

    def __getattr__(self, item):
        """proxy for underlying pool object"""
        desc = type(self).__dict__.get(item)
        if hasattr(desc, '__get__'):
            return desc.__get__(self)
        return getattr(self._pool, item)

    def submit(self, fn, *args, **kwargs):
        fut = self._pool.submit(fn, *args, **kwargs)
        self.futures.append(fut)
        return fut

    def map(self, fn, *iterables):
        self.futures.extend(self._pool.submit(fn, *args) for args in zip(*iterables))

    def dispatch(self, fn, *args, **kwargs):
        """run on thread pool but don't wait for completion"""
        return self._pool.submit(fn, *args, **kwargs)

    def __enter__(self):
        self.futures.clear()
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
    """manage a socket so it gets closed after exiting with block"""
    sock = socket(AF_INET, SOCK_DGRAM)
    try:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.settimeout(timeout)
        try:
            sock.bind(("", 0))  # allow OS to assign next available source port
        except Exception as err:
            raise ConnectionError(f'WorkflowException: error {str(err)} while trying to open socket')
        yield sock
    finally:
        sock.close()


def even_split(array: Iterable, n_splits: int) -> List[List]:
    """
    split array as evenly as possible

    note, flattening the result will not necessarily be in order of the original input

    similar to np.array_split, only for 1d arrays
    """
    res = [[] for _ in range(n_splits)]
    for v, r in zip(array, cycle(res)):
        r.append(v)
    return res


