import logging
from abc import ABC, abstractmethod
from functools import partial
from typing import List, Dict, Any, Optional, Union

from .settings import Waveform
from .colors import Color, ColorPower

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
    def set_color(self, color: Color, duration=0, rapid=rapid_default):
        """set color on color lights"""

    @abstractmethod
    def set_color_power(self, cp: ColorPower, duration=0, rapid=True):
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


class MultizoneAPI:
    @abstractmethod
    def set_zone_color(self, start, end, color, duration=0, rapid=rapid_default, apply=1):
        """set zone color on multizone lights"""

    @abstractmethod
    def set_zone_colors(self, colors, duration=0, rapid=rapid_default):
        """set zone colors on multizone lights"""
