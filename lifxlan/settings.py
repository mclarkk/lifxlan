from enum import Enum

from .errors import InvalidParameterException

unknown = 'UNKNOWN'
TOTAL_NUM_LIGHTS = 17
DEFAULT_KELVIN = 3200

class Waveform(Enum):
    saw = 0
    sine = 1
    half_sine = 2
    triangle = 3
    pulse = 4


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


Lights = {'living room 1': (0, 0),
          'living room 2': (0, 0),
          'living room 3': (0, 0),
          'living room 4': (0, 0),
          'kitchen 1': (0, 0),
          'kitchen 2': (0, 0),
          'kitchen 3': (0, 0),
          'kitchen 4': (0, 0),
          'creative space 1': (0, 0),
          'creative space 2': (0, 0),
          'creative space 3': (0, 0),
          'creative space 4': (0, 0),
          }
