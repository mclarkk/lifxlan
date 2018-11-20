from enum import Enum
from typing import NamedTuple

from lifxlan.errors import InvalidParameterException


class Color(NamedTuple):
    hue: int
    saturation: int
    brightness: int
    kelvin: int


class PowerSettings(Enum):
    on = (True, 1, "on", 65535)
    off = (False, 0, "off")

    @classmethod
    def validate(cls, value) -> int:
        if value in cls.on:
            return 65535
        elif value in cls.off:
            return 0
        raise InvalidParameterException(f'{value} is not a valid power level.')
