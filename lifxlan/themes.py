import logging
import random
from typing import List, Dict

import numpy as np

from .colors import Color, Colors

__author__ = 'acushner'

log = logging.getLogger(__name__)

Weight = int


class Theme:
    def __init__(self, colors: Dict[Color, Weight]):
        self._colors = colors

    @classmethod
    def from_colors(cls, *colors: Color):
        """create an equal weight theme from colors"""
        return cls(dict.fromkeys(colors, 1))

    @property
    def sum_weights(self):
        return sum(self._colors.values())

    def get_colors(self, num_lights=1) -> List[Color]:
        """
        get colors for `num_lights` lights

        allows an easy way for a `Group` to figure out which colors to apply to its lights
        """
        splits = np.array_split(range(num_lights), self.sum_weights)
        random.shuffle(splits)
        splits_iter = iter(splits)

        res = []
        for c, weight in self._colors.items():
            for _, split in zip(range(weight), splits_iter):
                res.extend([c] * len(split))
        return res

    def __iter__(self):
        return iter(self._colors)


class Themes:
    xmas = Theme({Colors.RED: 3, Colors.GREEN: 3, Colors.GOLD: 1})
    hanukkah = Theme.from_colors(Colors.HANUKKAH_BLUE, Colors.WHITE)
    steelers = Theme({Colors.STEELERS_GOLD: 2, Colors.STEELERS_BLUE: 2,
                      Colors.STEELERS_RED: 2, Colors.STEELERS_SILVER: 1})
    snes = Theme.from_colors(*Colors.by_name('SNES'))
