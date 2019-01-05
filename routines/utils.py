from typing import Optional, Union, Iterable

from lifxlan import init_log, Theme, Color

__author__ = 'acushner'

log = init_log(__name__)

ColorTheme = Optional[Union[Theme, Color, Iterable[Color]]]


def colors_to_theme(val: ColorTheme) -> Optional[Theme]:
    """convert a ColorTheme to Theme"""
    if isinstance(val, Color):
        return Theme.from_colors(val)
    if isinstance(val, Theme):
        return val
    if isinstance(val, Iterable):
        return Theme.from_colors(*val)
    return val


