import colorsys
import random
from collections import Counter
from enum import Enum
from typing import NamedTuple, Dict, Union, List

import numpy as np

from lifxlan.errors import InvalidParameterException

unknown = 'UNKNOWN'
TOTAL_NUM_LIGHTS = 13


class Waveform(Enum):
    saw = 0
    sine = 1
    half_sine = 2
    triangle = 3
    pulse = 4


class Color(NamedTuple):
    hue: int
    saturation: int
    brightness: int
    kelvin: int

    @classmethod
    def from_hex(cls, h, kelvin=3200):
        nums = []
        for _ in range(3):
            nums.append(h & 0xff)
            h >>= 8
        nums.reverse()
        h, s, b = colorsys.rgb_to_hsv(*nums)

        mult = 2 ** 16 - 1
        return cls(*map(int, (h * mult, s * mult, b / 255 * mult, kelvin)))


class PowerSettings(Enum):
    on = True, 1, "on", 65535
    off = False, 0, "off"

    @classmethod
    def validate(cls, value) -> int:
        if value in cls.on.value or (isinstance(value, int) and value):
            return cls.on.as_int
        elif value in cls.off.value:
            return cls.off.as_int
        raise InvalidParameterException(f'{value} is not a valid power level. valid levels:'
                                        f'\non: {cls.on.value}\noff: {cls.off.value}')

    @property
    def as_int(self):
        if self is PowerSettings.on:
            return 65535
        elif self is PowerSettings.off:
            return 0
        else:
            raise RuntimeError('you should never be here')


class ColorPower(NamedTuple):
    color: Color
    power: int


class ColorsMeta(type):
    def __iter__(cls):
        for name, val in vars(cls).items():
            if isinstance(val, Color):
                yield name, val

    def __getitem__(cls, item):
        return cls.__dict__[item]

    def __str__(cls):
        colors = '\n\t'.join(map(str, cls))
        return f'Colors:\n\t{colors}'


class Colors(metaclass=ColorsMeta):
    DEFAULT = Color(43520, 0, 39321, 3200)
    RED = Color(65535, 65535, 65535, 3500)
    ORANGE = Color(6500, 65535, 65535, 3500)
    YELLOW = Color(9000, 65535, 65535, 3500)
    GREEN = Color(16173, 65535, 65535, 3500)
    CYAN = Color(29814, 65535, 65535, 3500)
    BLUE = Color(43634, 65535, 65535, 3500)
    PURPLE = Color(50486, 65535, 65535, 3500)
    PINK = Color(58275, 65535, 47142, 3500)
    WHITE = Color(58275, 0, 65535, 5500)
    COLD_WHITE = Color(58275, 0, 65535, 9000)
    WARM_WHITE = Color(58275, 0, 65535, 3200)
    GOLD = Color(58275, 0, 65535, 2500)
    YALE_BLUE = Color.from_hex(0xf4d92)
    HANUKKAH_BLUE = Color.from_hex(0x09239b)
    STEELERS_GOLD = Color.from_hex(0xffb612)
    STEELERS_BLACK = Color.from_hex(0x101820)
    STEELERS_BLUE = Color.from_hex(0x00539b)
    STEELERS_RED = Color.from_hex(0xc60c30)
    STEELERS_SILVER = Color.from_hex(0xa5acaf)


Weight = int


# themes
class Theme:
    def __init__(self, colors: Dict[Color, Weight]):
        self._colors = colors

    @property
    def sum_weights(self):
        return sum(self._colors.values())

    def get_colors(self, num_lights=1) -> List[Color]:
        """get colors for `num_lights` lights"""
        splits = np.array_split(range(num_lights), self.sum_weights)
        random.shuffle(splits)
        splits_iter = iter(splits)

        res = []
        for c, weight in self._colors.items():
            for _, split in zip(range(weight), splits_iter):
                res.extend([c] * len(split))
        return res


class Themes:
    xmas = Theme({Colors.RED: 3, Colors.GREEN: 3, Colors.GOLD: 1})
    hanukkah = Theme({Colors.HANUKKAH_BLUE: 1, Colors.WHITE: 1})
    steelers = Theme({Colors.STEELERS_GOLD: 2, Colors.STEELERS_BLUE: 2,
                      Colors.STEELERS_RED: 2, Colors.STEELERS_SILVER: 1})
