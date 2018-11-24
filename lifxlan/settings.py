import colorsys
from enum import Enum
from typing import NamedTuple

from lifxlan.errors import InvalidParameterException

unknown = 'UNKNOWN'


class Color(NamedTuple):
    hue: int
    saturation: int
    brightness: int
    kelvin: int

    @classmethod
    def from_hex(cls, h, kelvin=9000):
        nums = []
        for _ in range(3):
            nums.append(h & 0xff)
            h >>= 8
        nums.reverse()
        h, s, b = colorsys.rgb_to_hsv(*nums)
        return cls(*map(int, (h * 2 ** 16, s * 2 ** 16, b / 255 * (2 ** 16), kelvin)))


class PowerSettings(Enum):
    on = True, 1, "on", 65535
    off = False, 0, "off"

    @classmethod
    def validate(cls, value) -> int:
        if value in cls.on.value:
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
