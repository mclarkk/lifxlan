import random
from copy import copy
from typing import List, Dict

from .colors import Color, Colors
from .utils import init_log, even_split

__author__ = 'acushner'

log = init_log(__name__)

Weight = int


class Theme:
    """
    weighted collection of colors
    """
    def __init__(self, colors: Dict[Color, Weight]):
        self._color_weights = colors

    def override_brightness(self, bright_pct):
        brightness = int(bright_pct / 100 * 65535)
        self._color_weights = {c._replace(brightness=brightness): w for c, w in self._color_weights.items()}
        return self

    @classmethod
    def from_colors(cls, *colors: Color):
        """create an equal weight theme from colors"""
        return cls(dict.fromkeys(colors, 1))

    @property
    def sum_weights(self):
        return sum(self._color_weights.values())

    def get_colors(self, num_lights=1) -> List[Color]:
        """
        get colors for `num_lights` lights

        allows an easy way for a `Group` to figure out which colors to apply to its lights
        """
        splits = even_split(range(num_lights), self.sum_weights)
        random.shuffle(splits)
        splits_iter = iter(splits)

        res = []
        for c, weight in self._color_weights.items():
            for _, split in zip(range(weight), splits_iter):
                res.extend([c] * len(split))
        random.shuffle(res)
        return res

    def __iter__(self):
        return iter(self._color_weights)

    def __add__(self, other):
        if isinstance(other, Color):
            other_cols = {other: 1}
        else:
            other_cols = other._color_weights

        return Theme({**self._color_weights, **other_cols})


class ThemesMeta(type):
    def __getattribute__(cls, item):
        res = type.__getattribute__(cls, item)
        if isinstance(res, Theme):
            res = copy(res)
        return res


class Themes(metaclass=ThemesMeta):
    xmas = Theme({Colors.XMAS_RED: 3, Colors.XMAS_GREEN: 3, Colors.XMAS_GOLD: 2})
    hanukkah = Theme.from_colors(Colors.HANUKKAH_BLUE, Colors.WHITE)
    steelers = Theme({Colors.STEELERS_GOLD: 3, Colors.STEELERS_BLUE: 1,
                      Colors.STEELERS_RED: 1, Colors.STEELERS_SILVER: 1})
    snes = Theme.from_colors(*Colors.by_name('SNES'))
    copilot = Theme.from_colors(*Colors.by_name('copilot'))
