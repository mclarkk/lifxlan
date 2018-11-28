# Useful to have, non-LAN functions
# Rev 0.1
# Date 06/08/2017
# Author: BHCunningham
#
# 1) RGB to HSBK conversion function
#
import time
from collections import deque
from concurrent.futures import wait
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps
from typing import Optional, List, Generator


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            print(f'func {func.__name__!r} took {time.time() - start_time} seconds')

    return wrapper


class WaitPool:
    """
    allow jobs to be submitted to either an existing pool or a dynamically-created one,
    wait for it to complete, and have access to the futures outside the `with` block

    """
    threads_per_pool = 8

    def __init__(self, pool: Optional[ThreadPoolExecutor] = None):
        self._pool = pool or ThreadPoolExecutor(self.threads_per_pool)
        self._futures = []

    @property
    def futures(self):
        return self._futures

    def wait(self):
        wait(self._futures)

    def __getattr__(self, item):
        """proxy for underlying pool object"""
        return getattr(self._pool, item)

    def map(self, fn, *iterables):
        self._futures.extend(self._pool.submit(fn, *args) for args in zip(*iterables))

    def submit(self, fn, *args, **kwargs):
        fut = self._pool.submit(fn, *args, **kwargs)
        self._futures.append(fut)
        return fut

    def __enter__(self):
        self._futures.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()


def exhaust_map(fn, *iterables):
    """
    map that gets executed immediately with the results discarded

    should be used for side effects (printing, updating, submitting to job pool, etc)
    """
    return exhaust(map(fn, *iterables))


def exhaust(iterable):
    deque(iterable, maxlen=0)


exhaust.__doc__ = exhaust_map.__doc__


### Convert an RGB colour definition to HSBK
# Author : BHCunningham
# Input: (Red, Green, Blue), Temperature
# Colours = 0 -> 255
# Temperature 2500-9000 K, 3500 is default.
# Output: (Hue, Saturation, Brightness, Temperature)

def RGBtoHSBK(RGB, temperature=3500):
    cmax = max(RGB)
    cmin = min(RGB)
    cdel = cmax - cmin

    brightness = int((cmax / 255) * 65535)

    if cdel != 0:
        saturation = int(((cdel) / cmax) * 65535)

        redc = (cmax - RGB[0]) / (cdel)
        greenc = (cmax - RGB[1]) / (cdel)
        bluec = (cmax - RGB[2]) / (cdel)

        if RGB[0] == cmax:
            hue = bluec - greenc
        else:
            if RGB[1] == cmax:
                hue = 2 + redc - bluec
            else:
                hue = 4 + greenc - redc

        hue = hue / 6
        if hue < 0:
            hue = hue + 1

        hue = int(hue * 65535)
    else:
        saturation = 0
        hue = 0

    return hue, saturation, brightness, temperature
