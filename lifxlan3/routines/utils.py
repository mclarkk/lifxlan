from functools import partial, wraps
from typing import Optional, Union, Iterable

from lifxlan3 import init_log, Theme, Color, global_settings

__author__ = 'acushner'

log = init_log(__name__)

ColorTheme = Optional[Union[Theme, Color, Iterable[Color]]]


def colors_to_theme(val: ColorTheme) -> Theme:
    """convert a ColorTheme to Theme"""
    if isinstance(val, Color):
        return Theme.from_colors(val)
    if isinstance(val, Theme):
        return val
    if isinstance(val, Iterable):
        return Theme.from_colors(*val)
    return val


def preserve_brightness(func=None, *, pb=True, reset=True):
    """decorator to prevent changing the existing brightness settings on lights"""
    if not func:
        return partial(func, pb=pb, reset=reset)

    @wraps(func)
    def wrapper(*args, **kwargs):
        orig = global_settings['preserve_brightness']
        global_settings['preserve_brightness'] = pb
        try:
            return func(*args, **kwargs)
        finally:
            if reset:
                global_settings['preserve_brightness'] = orig

    return wrapper


