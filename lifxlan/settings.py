import colorsys
import random
from enum import Enum
from functools import reduce
from typing import NamedTuple, Dict, List

import numpy as np

from lifxlan.errors import InvalidParameterException

unknown = 'UNKNOWN'
TOTAL_NUM_LIGHTS = 13
DEFAULT_KELVIN = 3200


class Waveform(Enum):
    saw = 0
    sine = 1
    half_sine = 2
    triangle = 3
    pulse = 4


class RGBk(NamedTuple):
    r: int
    g: int
    b: int
    k: int = DEFAULT_KELVIN

    @property
    def hex(self) -> str:
        """loses kelvin in this conversion"""
        return hex((self.r << 16) + (self.g << 8) + self.b)

    @property
    def color(self) -> 'Color':
        return Color.from_rgb(self)

    def __add__(self, other) -> 'RGBk':
        add = lambda v1, v2: round(((v1 ** 2 + v2 ** 2) / 2) ** .5)
        return RGBk(add(self.r, other.r), add(self.g, other.g), add(self.b, other.b), (self.k + other.k) // 2)


class Color(NamedTuple):
    hue: int
    saturation: int
    brightness: int
    kelvin: int = DEFAULT_KELVIN

    _mult = 2 ** 16

    @classmethod
    def from_hex(cls, h, kelvin=DEFAULT_KELVIN) -> 'Color':
        nums = []
        for _ in range(3):
            nums.append(h & 0xff)
            h >>= 8
        nums.reverse()
        return cls.from_rgb(RGBk(*nums, kelvin))

    @classmethod
    def from_rgb(cls, rgb: RGBk) -> 'Color':
        h, s, b = colorsys.rgb_to_hsv(*rgb[:3])
        mult = cls._mult - 1
        return cls(*map(round, (h * mult, s * mult, b / 255 * mult, rgb.k)))

    @property
    def hex(self) -> str:
        return self.rgb.hex

    @property
    def rgb(self) -> RGBk:
        mult = self._mult - 1
        h, s, b = self.hue / mult, self.saturation / mult, self.brightness / mult * 255
        return RGBk(*map(round, colorsys.hsv_to_rgb(h, s, b)), self.kelvin)

    def offset_hue(self, degrees) -> 'Color':
        hue_d = self.hue / self._mult * 360
        return self._replace(hue=round(abs((hue_d + degrees) % 360) * self._mult / 360))

    def __add__(self, other) -> 'Color':
        """avg colors together using math"""
        return (self.rgb + other.rgb).color

    @classmethod
    def mean(cls, *colors):
        return reduce(cls.__add__, colors)


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
            raise RuntimeError('you should not be here')


class ColorPower(NamedTuple):
    color: Color
    power: int


class ColorsMeta(type):
    def __iter__(cls):
        yield from ((name, val)
                    for name, val in vars(cls).items()
                    if isinstance(val, Color))

    def __getitem__(cls, item):
        return cls.__dict__[item]

    def __str__(cls):
        colors = '\n\t'.join(map(str, cls))
        return f'Colors:\n\t{colors}'


class Colors(metaclass=ColorsMeta):
    DEFAULT = Color(43520, 0, 39321)
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
    WARM_WHITE = Color(58275, 0, 65535)
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
