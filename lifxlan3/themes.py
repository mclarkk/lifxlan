import random
from copy import copy
from typing import List, Dict

from .colors import Color, Colors, LifxColors
from .utils import init_log, even_split

__author__ = 'acushner'

log = init_log(__name__)

Weight = int


class Theme:
    """weighted collection of colors"""

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
        colors = [c for c, w in self._color_weights.items()
                  for _ in range(w)]
        mult, rem = divmod(num_lights, len(colors))
        mult += bool(rem)
        return random.sample(colors * mult, num_lights)

    def __iter__(self):
        return iter(self._color_weights)

    def keys(self):
        return self._color_weights.keys()

    def values(self):
        return self._color_weights.values()

    def items(self):
        return self._color_weights.items()

    def __add__(self, other):
        if isinstance(other, Color):
            other_colors = {other: 1}
        elif isinstance(other, dict):
            other_colors = other
        elif isinstance(other, Theme):
            other_colors = other._color_weights
        else:
            return NotImplemented

        return Theme({**self._color_weights, **other_colors})

    def __iadd__(self, other):
        self._color_weights = (self + other)._color_weights
        return self

    def color_str(self, s):
        colors = ''.join(c.color_str(v * 4 * " ", set_bg=True) for c, v in self._color_weights.items())
        return f'{s:17}|{colors}|'


class ThemesMeta(type):
    """make `Themes` class more accessible"""

    def __getattribute__(cls, item):
        """copy a theme when accessed so that the original theme can't be mutated"""
        res = type.__getattribute__(cls, item)
        if isinstance(res, Theme):
            res = copy(res)
        return res

    def __iter__(cls):
        return ((name, theme)
                for name, theme in cls.__dict__.items()
                if isinstance(theme, Theme))

    def __getitem__(cls, item):
        return cls.__dict__[item]

    def get(cls, val, item=None):
        if val in cls.__dict__:
            return cls[val]
        return item


class Themes(metaclass=ThemesMeta):
    """class for all pre-fab themes"""
    copilot = Theme.from_colors(*Colors.by_name('copilot'))
    easter = Theme.from_colors(*map(Color.from_hex, (0x28bb94, 0x66ddab, 0x612a6c, 0x421b52, 0xdb95c7, 0xd1719c)))
    eid = Theme.from_colors(Colors.GREEN, Colors.WHITE)
    hanukkah = Theme.from_colors(Colors.HANUKKAH_BLUE, Colors.WHITE)
    july_4th = Theme.from_colors(Color.from_hex(0xe0162b), Colors.WHITE, Color.from_hex(0x0052a5))
    mario = Theme.from_colors(*Colors.by_name('mario'))
    python = (Theme.from_colors(*Colors.by_name('python')) + {Colors.PYTHON_DARK_BLUE: 2, Colors.PYTHON_LIGHT_BLUE: 2})
    rainbow = Theme.from_colors(Colors.RED, Colors.ORANGE, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE,
                                Colors.PURPLE, Colors.PINK)
    rainbow_2 = Theme.from_colors(*map(Color.from_hex, (0x401b86, 0x2546c9, 0x2ad424, 0xf0ec25, 0xf07537, 0xdb3a4c)))
    snes = Theme.from_colors(*Colors.by_name('SNES'))
    steelers = Theme({Colors.STEELERS_GOLD: 3, Colors.STEELERS_BLUE: 1,
                      Colors.STEELERS_RED: 1, Colors.STEELERS_SILVER: 1})
    whites = Theme.from_colors(LifxColors.CoolWhite, LifxColors.WarmWhite, LifxColors.White, LifxColors.CoolWhite,
                               LifxColors.Daylight)
    xmas = Theme({Colors.XMAS_RED: 3, Colors.XMAS_GREEN: 3, Colors.XMAS_GOLD: 2})
    xmas_lighter = xmas + {Colors.DEFAULT: 3}
    st_paddys = Theme.from_colors(Colors.MARIO_GREEN, Colors.WARM_WHITE)
