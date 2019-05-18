from enum import Enum

UNKNOWN = 'UNKNOWN'
TOTAL_NUM_LIGHTS = 22
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


_global_dict = {}


class GlobalSettings:
    """
    proxy because i can't import `Colors` here
    and it makes it possible to update these values as the program is running
    """

    @property
    def _global(self):
        from lifxlan import Colors
        if not _global_dict:
            _global_dict['library'] = Colors.DEFAULT._replace(kelvin=3634)
            _global_dict['preserve_brightness'] = False
        return _global_dict

    def __getitem__(self, item):
        return self._global[item]

    def __setitem__(self, key, value):
        self._global[key] = value

    def get(self, item, default=None):
        if item in self._global:
            return self[item]
        return default


global_settings = GlobalSettings()
