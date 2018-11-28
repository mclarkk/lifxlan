# import thread
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from functools import partial, wraps
from typing import List

from .multizonelight import MultiZoneLight
from .settings import Color, Waveform
from .utils import WaitPool, exhaust
from .light import Light
from .device import Device
from .tilechain import TileChain


def _set_generic(func=None, *, light_type='color_lights'):
    """
    call the wrapped `func.__name__` on all lights in the given `lights_name` argument
    essentially acts as a passthrough to the underlying light objects themselves
    """
    if func is None:
        return partial(_set_generic, light_type=light_type)

    @wraps(func)
    def wrapper(self: 'Group', *args, **kwargs):
        with self._wait_pool as wp:
            exhaust(wp.submit(getattr(l, func.__name__), *args, **kwargs) for l in getattr(self, light_type))
        return self._wait_pool.futures

    return wrapper


class Group(object):

    def __init__(self, devices: List[Device]):
        self.devices = devices
        self._wait_pool = WaitPool(ThreadPoolExecutor(30))

    # noinspection PyTypeChecker
    @property
    def lights(self) -> List[Light]:
        return [l for l in self.devices if l.is_light]

    # noinspection PyTypeChecker
    @property
    def color_lights(self) -> List[Light]:
        return [l for l in self.devices if l.supports_color]

    # noinspection PyTypeChecker
    @property
    def multizone_lights(self) -> List[MultiZoneLight]:
        return [l for l in self.devices if l.supports_multizone]

    # noinspection PyTypeChecker
    @property
    def infrared_lights(self) -> List[Light]:
        return [l for l in self.devices if l.supports_infrared]

    # noinspection PyTypeChecker
    @property
    def tilechain_lights(self) -> List[TileChain]:
        return [l for l in self.devices if l.supports_chain]

    def refresh(self):
        with self._wait_pool as wp:
            exhaust(wp.submit(d.refresh) for d in self.devices)

    def add_device(self, device_object):
        if device_object not in self.devices:
            self.devices.append(device_object)

    def remove_device(self, device_object):
        with suppress(ValueError):
            self.devices.remove(device_object)

    def remove_device_by_name(self, device_name):
        self.devices[:] = [d for d in self.devices if d.label != device_name]

    def set_power(self, power, duration=0, rapid=False):
        with self._wait_pool as wp:
            wp.map(self._set_power_helper, ((d, power, duration, rapid) for d in self.devices))

    @staticmethod
    def _set_power_helper(device, power, duration, rapid):
        if device.is_light:
            device.set_power(power, duration, rapid)
        else:
            device.set_power(power, rapid)

    @_set_generic
    def set_waveform(self, is_transient, color: Color, period, cycles, duty_cycle, waveform: Waveform, rapid=False):
        """set waveform on color lights"""

    @_set_generic
    def set_color(self, color: Color, duration=0, rapid=False):
        """set color on color lights"""

    @_set_generic
    def set_hue(self, hue, duration=0, rapid=False):
        """set hue on color lights"""

    @_set_generic
    def set_brightness(self, brightness, duration=0, rapid=False):
        """set brightness on color lights"""

    @_set_generic
    def set_saturation(self, saturation, duration=0, rapid=False):
        """set saturation on color lights"""

    @_set_generic
    def set_kelvin(self, kelvin, duration=0, rapid=False):
        """set kelvin on color lights"""

    @_set_generic
    def set_infrared(self, infrared_brightness):
        """set infrared on color lights"""

    @_set_generic(light_type='multizone_lights')
    def set_zone_color(self, start, end, color, duration=0, rapid=False, apply=1):
        """set zone color on multizone lights"""

    @_set_generic(light_type='multizone_lights')
    def set_zone_colors(self, colors, duration=0, rapid=False):
        """set zone colors on multizone lights"""

    def __len__(self):
        return len(self.devices)

    def __iter__(self):
        return iter(self.devices)

    def __str__(self):
        s = "Group ({}):\n\n".format(len(self.devices))
        for d in self.devices:
            s += str(d) + "\n"
        return s
