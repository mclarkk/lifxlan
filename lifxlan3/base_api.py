import logging
from abc import ABC, abstractmethod

from .colors import Color, ColorPower
from .settings import Waveform

__author__ = 'acushner'

log = logging.getLogger(__name__)


def __main():
    pass


if __name__ == '__main__':
    __main()

rapid_default = True


class LightAPI(ABC):
    @abstractmethod
    def set_waveform(self, waveform: Waveform, color: Color, period_msec, num_cycles,
                     *, skew_ratio=.5, is_transient=True, rapid=False):
        """set waveform on color lights"""

    @abstractmethod
    def set_color(self, color: Color, duration=0, rapid=rapid_default, preserve_brightness: bool = None):
        """set color on color lights"""

    @abstractmethod
    def set_color_power(self, cp: ColorPower, duration=0, rapid=True, preserve_brightness: bool = None):
        """set color and power on color lights"""

    @abstractmethod
    def set_hue(self, hue, duration=0, rapid=rapid_default, offset=False):
        """set hue on color lights"""

    @abstractmethod
    def set_brightness(self, brightness, duration=0, rapid=rapid_default, offset=False):
        """set brightness on color lights"""

    @abstractmethod
    def set_saturation(self, saturation, duration=0, rapid=rapid_default, offset=False):
        """set saturation on color lights"""

    @abstractmethod
    def set_kelvin(self, kelvin, duration=0, rapid=rapid_default, offset=False):
        """set kelvin on color lights"""

    @abstractmethod
    def set_infrared(self, infrared_brightness):
        """set infrared on color lights"""

    @abstractmethod
    def turn_on(self, duration=0):
        """turn on lights"""

    @abstractmethod
    def turn_off(self, duration=0):
        """turn off lights"""
