import colorsys
import operator as op
from functools import reduce, wraps
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

    def color_str(self, s, set_bg=False) -> str:
        """
        create str with different foreground(default)/background color for use in terminal
        reset to default at end of str
        """
        layer = sty.bg if set_bg else sty.fg
        return f'{layer(*self[:3])}{s}{layer.rs}'

    @staticmethod
    def _add_components(v1, v2):
        return int(((v1**2 + v2**2) / 2) ** 0.5)

    def __add__(self, other) -> 'RGBk':
        add = self._add_components
        return RGBk(
            add(self.r, other.r),
            add(self.g, other.g),
            add(self.b, other.b),
            (self.k + other.k) // 2,
        )


def _replace(func):
    @wraps(func)
    def wrapper(self, val):
        return self._replace(**{func.__name__[2:]: val})

    return wrapper


class Color(NamedTuple):
    hue: int
    saturation: int
    brightness: int
    kelvin: int = DEFAULT_KELVIN

    @_replace
    def r_hue(self, val):
        """replace hue"""

    @_replace
    def r_saturation(self, val):
        """replace saturation"""

    @_replace
    def r_brightness(self, val):
        """replace brightness"""

    @_replace
    def r_kelvin(self, val):
        """replace kelvin"""

    _mult = 2**16
    _max_complements = 1024

    # ==================================================================================================================
    # CREATE COLORS FROM OTHER COLOR SPACES
    # ==================================================================================================================

    @classmethod
    def from_hex(cls, h, kelvin=DEFAULT_KELVIN) -> 'Color':
        nums = []
        for _ in range(3):
            nums.append(h & 0xFF)
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

    def color_str(self, s, set_bg=False) -> str:
        """
        create str with different foreground(default)/background color for use in terminal
        reset to default at end of str
        """
        return self.rgb.color_str(s, set_bg)

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

            warn(
                f'exceeded max number of complements: {self._max_complements}, something may have gone wrong'
            )

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
        return ((name, val) for name, val in vars(cls).items() if isinstance(val, Color))

    def __getitem__(cls, item):
        return cls.__dict__[item]

    def __str__(cls):
        colors = '\n\t'.join(map(str, cls))
        return f'{cls.__name__}:\n\t{colors}'

    def sum(cls, *colors: Color) -> Color:
        """average together all colors provided"""
        return reduce(op.add, colors)

    def by_name(cls, name) -> List[Color]:
        """get colors if they contain `name` in their name"""
        name = name.lower()
        return [c for n, c in cls if name in n.lower()]


class Colors(metaclass=ColorsMeta):
    DEFAULT = Color(43520, 0, 39321, 3200)
    OFF = Color(0, 0, 0, 0)

    RED = Color(65535, 65535, 65535, 3500)
    ORANGE = Color(6500, 65535, 65535, 3500)
    YELLOW = Color(9000, 65535, 65535, 3500)
    GREEN = Color(16173, 65535, 65535, 3500)
    CYAN = Color(29814, 65535, 65535, 3500)
    BLUE = Color(43634, 65535, 65535, 3500)
    PURPLE = Color(50486, 65535, 65535, 3500)
    MAGENTA = Color.from_hex(0xFF00FF)
    PINK = Color(58275, 65535, 47142, 3500)

    WHITE = Color(58275, 0, 65535, 5500)
    COLD_WHITE = Color(58275, 0, 65535, 9000)
    WARM_WHITE = Color(58275, 0, 65535, 3200)
    GOLD = Color(58275, 0, 65535, 2500)
    BROWN = Color.from_hex(0xA0522D)

    COPILOT_BLUE = Color.from_hex(0x00B4E3)
    COPILOT_BLUE_GREEN = Color.from_hex(0x00827D)
    COPILOT_BLUE_GREY = Color.from_hex(0x386E8F)
    COPILOT_DARK_BLUE = Color.from_hex(0x193849)

    HANUKKAH_BLUE = Color.from_hex(0x09239B)

    MARIO_BLUE = Color.from_hex(0x049CD8)
    MARIO_YELLOW = Color.from_hex(0xFBD000)
    MARIO_RED = Color.from_hex(0xE52521)
    MARIO_GREEN = Color.from_hex(0x43B047)

    PYTHON_LIGHT_BLUE = Color.from_hex(0x4B8BBE)
    PYTHON_DARK_BLUE = Color.from_hex(0x306998)
    PYTHON_LIGHT_YELLOW = Color.from_hex(0xFFE873)
    PYTHON_DARK_YELLOW = Color.from_hex(0xFFD43B)
    PYTHON_GREY = Color.from_hex(0x646464)

    SNES_BLACK = Color.from_hex(0x211A21)
    SNES_DARK_GREY = Color.from_hex(0x908A99)
    SNES_DARK_PURPLE = Color.from_hex(0x4F43AE)
    SNES_LIGHT_GREY = Color.from_hex(0xCEC9CC)
    SNES_LIGHT_PURPLE = Color.from_hex(0xB5B6E4)

    STEELERS_BLACK = Color.from_hex(0x101820)
    STEELERS_BLUE = Color.from_hex(0x00539B)
    STEELERS_GOLD = Color.from_hex(0xFFB612)
    STEELERS_RED = Color.from_hex(0xC60C30)
    STEELERS_SILVER = Color.from_hex(0xA5ACAF)

    XMAS_GOLD = Color.from_hex(0xE5D08F)
    XMAS_GREEN = Color.from_hex(0x18802B)
    XMAS_RED = Color.from_hex(0xD42426)

    YALE_BLUE = Color.from_hex(0xF4D92)


class LifxColors(metaclass=ColorsMeta):
    """colors available via voice from lifx"""

    WarmWhite = Color(hue=54612, saturation=0, brightness=32767, kelvin=2500)
    SoftWhite = Color(hue=54612, saturation=0, brightness=32767, kelvin=2700)
    White = Color(hue=54612, saturation=0, brightness=32767, kelvin=4000)
    Daylight = Color(hue=54612, saturation=0, brightness=32767, kelvin=5500)
    CoolWhite = Color(hue=54612, saturation=0, brightness=32767, kelvin=7000)

    Blue = Color(hue=43690, saturation=65535, brightness=65535, kelvin=2500)
    Crimson = Color(hue=63350, saturation=59551, brightness=65535, kelvin=2500)
    Cyan = Color(hue=32767, saturation=65535, brightness=65535, kelvin=2500)
    Fuchsia = Color(hue=54612, saturation=65535, brightness=65535, kelvin=2500)
    Gold = Color(hue=9102, saturation=65535, brightness=65535, kelvin=2500)
    Green = Color(hue=21845, saturation=65535, brightness=65535, kelvin=2500)
    Lavender = Color(hue=46420, saturation=32767, brightness=65535, kelvin=2500)
    Lime = Color(hue=13653, saturation=57670, brightness=65535, kelvin=2500)
    Magenta = Color(hue=54612, saturation=65535, brightness=65535, kelvin=2500)
    Orange = Color(hue=7099, saturation=65535, brightness=65535, kelvin=2500)
    Pink = Color(hue=63350, saturation=16449, brightness=65535, kelvin=2500)
    Purple = Color(hue=50425, saturation=56484, brightness=65535, kelvin=7000)
    Red = Color(hue=0, saturation=65535, brightness=65535, kelvin=7000)
    Salmon = Color(hue=3094, saturation=34078, brightness=65535, kelvin=7000)
    SkyBlue = Color(hue=35862, saturation=27727, brightness=65535, kelvin=7000)
    Teal = Color(hue=32767, saturation=65535, brightness=65535, kelvin=7000)
    Turquoise = Color(hue=31675, saturation=47106, brightness=65535, kelvin=7000)
    Violet = Color(hue=54612, saturation=29589, brightness=65535, kelvin=7000)


class ColorPower(NamedTuple):
    color: Color
    power: int
