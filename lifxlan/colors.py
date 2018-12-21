import colorsys
import operator as op
from functools import reduce
from typing import List, NamedTuple

import sty

from .settings import DEFAULT_KELVIN
from .utils import init_log

__author__ = 'acushner'

log = init_log(__name__)


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

    @staticmethod
    def _add_components(v1, v2):
        return int(((v1 ** 2 + v2 ** 2) / 2) ** .5)

    def __add__(self, other) -> 'RGBk':
        add = self._add_components
        return RGBk(add(self.r, other.r), add(self.g, other.g), add(self.b, other.b), (self.k + other.k) // 2)


class Color(NamedTuple):
    hue: int
    saturation: int
    brightness: int
    kelvin: int = DEFAULT_KELVIN

    _mult = 2 ** 16
    _max_complements = 1024

    # ==================================================================================================================
    # CREATE COLORS FROM OTHER COLOR SPACES
    # ==================================================================================================================

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
        return cls(*map(int, (h * mult, s * mult, b / 255 * mult, rgb.k)))

    # ==================================================================================================================
    # COLOR PROPERTIES
    # ==================================================================================================================
    @property
    def hex(self) -> str:
        return self.rgb.hex

    @property
    def rgb(self) -> RGBk:
        mult = self._mult - 1
        h, s, b = self.hue / mult, self.saturation / mult, self.brightness / mult * 255
        return RGBk(*map(int, colorsys.hsv_to_rgb(h, s, b)), self.kelvin)

    @property
    def bounded(self) -> 'Color':
        """force values into acceptable ranges - rotate around when exceeded"""
        k = (self.kelvin - 2500) % (9000 - 2500) + 2500
        return Color(*map(self._to_2_16, self[:3]), k)

    @property
    def clamped(self) -> 'Color':
        """force values into acceptable ranges - min/max when exceeded"""
        k = min(max(self.kelvin, 2500), 9000)
        return Color(*map(self._validate_hsb, self[:3]), k)

    def color_str(self, s, set_fg=True) -> str:
        layer = sty.fg if set_fg else sty.bg
        return f'{layer(*self.rgb[:3])}{s}{layer.rs}'

    # ==================================================================================================================
    # COLOR METHODS
    # ==================================================================================================================

    def offset_hue(self, degrees) -> 'Color':
        hue = self._to_2_16(self.hue + degrees / 360 * self._mult)
        return self._replace(hue=hue)

    def get_complements(self, degrees) -> List['Color']:
        """
        return list of colors offset by degrees

        this list will contain all unique colors that can be produced by this
        degree offset (i.e., it will keep offsetting until it makes it around the color wheel,
        perhaps multiple times, back to the starting point)

        useful because it avoids rounding errors that can occur by doing something like:
        >>> c = Colors.YALE_BLUE
        >>> for _ in range(1000):
        >>>     c = c.offset_hue(30)
        """
        res = [self]
        for n in range(1, self._max_complements):
            n_deg = n * degrees
            if n_deg % 360 == 0:
                break

            res.append(self.offset_hue(n_deg))
        else:
            from warnings import warn
            warn(f'exceeded max number of complements: {self._max_complements}, something may have gone wrong')

        return res

    @staticmethod
    def _to_2_16(val):
        """force val to be between 0 and 65535 inclusive, rotate"""
        return int(min(65535, val % Color._mult))

    @staticmethod
    def _validate_hsb(val) -> int:
        """clamp to range [0, 65535]"""
        return int(min(max(val, 0), 65535))

    # ==================================================================================================================
    # ADD COLORS TOGETHER
    # ==================================================================================================================
    def __add__(self, other) -> 'Color':
        """avg colors together using math"""
        return (self.rgb + other.rgb).color

    def __iadd__(self, other):
        return self + other


class ColorsMeta(type):
    """make `Colors` more accessible"""

    def __iter__(cls):
        return ((name, val)
                for name, val in vars(cls).items()
                if isinstance(val, Color))

    def __getitem__(cls, item):
        return cls.__dict__[item]

    def __str__(cls):
        colors = '\n\t'.join(map(str, cls))
        return f'{cls.__name__}:\n\t{colors}'


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
    BROWN = Color.from_hex(0xa0522d)

    COPILOT_BLUE = Color.from_hex(0x00b4e3)
    COPILOT_BLUE_GREEN = Color.from_hex(0x00827d)
    COPILOT_BLUE_GREY = Color.from_hex(0x386e8f)
    COPILOT_DARK_BLUE = Color.from_hex(0x193849)

    HANUKKAH_BLUE = Color.from_hex(0x09239b)

    MARIO_BLUE = Color.from_hex(0x049cd8)
    MARIO_YELLOW = Color.from_hex(0xfbd000)
    MARIO_RED = Color.from_hex(0xe52521)
    MARIO_GREEN = Color.from_hex(0x43b047)

    PYTHON_LIGHT_BLUE = Color.from_hex(0x4b8bbe)
    PYTHON_DARK_BLUE = Color.from_hex(0x306998)
    PYTHON_LIGHT_YELLOW = Color.from_hex(0xffe873)
    PYTHON_DARK_YELLOW = Color.from_hex(0xffd43b)
    PYTHON_GREY = Color.from_hex(0x646464)

    SNES_BLACK = Color.from_hex(0x211a21)
    SNES_DARK_GREY = Color.from_hex(0x908a99)
    SNES_DARK_PURPLE = Color.from_hex(0x4f43ae)
    SNES_LIGHT_GREY = Color.from_hex(0xcec9cc)
    SNES_LIGHT_PURPLE = Color.from_hex(0xb5b6e4)

    STEELERS_BLACK = Color.from_hex(0x101820)
    STEELERS_BLUE = Color.from_hex(0x00539b)
    STEELERS_GOLD = Color.from_hex(0xffb612)
    STEELERS_RED = Color.from_hex(0xc60c30)
    STEELERS_SILVER = Color.from_hex(0xa5acaf)

    XMAS_GOLD = Color.from_hex(0xe5d08f)
    XMAS_GREEN = Color.from_hex(0x18802b)
    XMAS_RED = Color.from_hex(0xd42426)

    YALE_BLUE = Color.from_hex(0xf4d92)

    @classmethod
    def sum(cls, *colors: Color) -> Color:
        """average together all colors provided"""
        return reduce(op.add, colors)

    @classmethod
    def by_name(cls, name) -> List[Color]:
        """get colors if they contain `name` in their name"""
        name = name.lower()
        return [c for n, c in cls if name in n.lower()]


class ColorPower(NamedTuple):
    color: Color
    power: int
