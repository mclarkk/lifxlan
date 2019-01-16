from enum import Enum

unknown = 'UNKNOWN'
TOTAL_NUM_LIGHTS = 21
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
        raise ValueError(f'{value} is not a valid power level. valid levels:'
                         f'\non: {cls.on.value}\noff: {cls.off.value}')

    @property
    def as_int(self):
        if self is PowerSettings.on:
            return 65535
        elif self is PowerSettings.off:
            return 0
        else:
            raise RuntimeError('you should not be here')


class DefaultOverride(dict):
    """proxy"""

    @property
    def _override(self):
        from lifxlan import Colors
        return {
            'library': Colors.DEFAULT._replace(kelvin=3634)
        }

    def __getattribute__(self, item):
        override = super().__getattribute__('_override')
        return getattr(override, item)


default_override = DefaultOverride()
