# import thread
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from functools import partial, wraps
from itertools import chain
from typing import List, Union, Dict, Optional, Iterable

from .device import Device
from .light import Light
from .settings import Color, Waveform, Theme, ColorPower, TOTAL_NUM_LIGHTS
from .utils import WaitPool, exhaust


def _set_generic(func=None, *, func_name_override=None, light_type='color_lights'):
    """
    call the wrapped `func.__name__` on all lights in the given
    `light_type` argument essentially acts as a passthrough to the
    underlying light objects themselves

    changing `light_type` in the decorator call will allow you to
    forward calls to multizone and tile lights
    """
    if func is None:
        return partial(_set_generic, light_type=light_type, func_name_override=func_name_override)
    func_name = func_name_override or func.__name__

    @wraps(func)
    def wrapper(self: 'Group', *args, **kwargs):
        with self._wait_pool as wp:
            exhaust(wp.submit(getattr(l, func_name), *args, **kwargs) for l in getattr(self, light_type))
        return self._wait_pool.futures

    return wrapper


class _GetGeneric:
    """based on member name and light type, create a dictionary of {Light: attr}"""

    def __set_name__(self, owner, name):
        self.name = name

    def __init__(self, light_type='color_lights'):
        self.light_type = light_type

    def __get__(self, instance, owner):
        if not instance:
            return self

        return {d: getattr(d, self.name) for d in getattr(instance, self.light_type)}


class Group:

    def __init__(self, devices: Iterable[Device], name: Optional[str] = None):
        self.devices = self._init_devices(devices)
        self.name = name or ''
        self._wait_pool = WaitPool(ThreadPoolExecutor(TOTAL_NUM_LIGHTS))

    @staticmethod
    def _init_devices(devices):
        """ensure no duplicates and preserve original order"""
        seen = set()
        return sorted(d for d in devices if d not in seen and not seen.add(d))

    def refresh(self):
        with self._wait_pool as wp:
            futures = {d: wp.submit(d.refresh) for d in self.devices}

        for d, fut in futures.items():
            if not fut.result():
                print(f'ERROR with device with name, mac addr {d.label, d.mac_addr}, '
                      f'removing from group. result: {fut.result()}')
                self.remove_device(d)

    # ==================================================================================================================
    # GROUP PROPERTIES
    # ==================================================================================================================

    # noinspection PyTypeChecker
    @property
    def lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.is_light)

    # noinspection PyTypeChecker
    @property
    def color_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_color)

    # noinspection PyTypeChecker
    @property
    def multizone_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_multizone)

    # noinspection PyTypeChecker
    @property
    def infrared_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_infrared)

    # noinspection PyTypeChecker
    @property
    def tilechain_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_chain)

    # ==================================================================================================================
    # ALTER GROUP IN MEMORY
    # ==================================================================================================================

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
            exhaust(wp.submit(self._set_power_helper, d, power, duration, rapid) for d in self.devices)

    # ==================================================================================================================
    # SET LIGHT VALUES IN GROUP
    # ==================================================================================================================

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

    def set_color_power(self, cp: Union[ColorPower, Dict[Light, ColorPower]],
                        duration=0, rapid=True):
        """set color and power on color lights"""
        if isinstance(cp, ColorPower):
            return self._set_color_power(cp, duration, rapid)

        with self._wait_pool as wp:
            exhaust(wp.submit(l.set_color_power, _cp, duration, rapid) for l, _cp in cp.items())

    @_set_generic(func_name_override='set_color_power')
    def _set_color_power(self, cp: ColorPower, duration=0, rapid=True):
        """set color and power on color lights"""

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

    def set_theme(self, theme: Theme, power_on=True, duration=0, rapid=True):
        colors = theme.get_colors(len(self))
        with self._wait_pool as wp:
            exhaust(
                wp.submit(l.set_color_power, ColorPower(c, power_on), duration, rapid) for l, c in zip(self, colors))

    # ==================================================================================================================
    # GET SETTINGS FROM LIGHTS
    # ==================================================================================================================
    power = _GetGeneric('devices')
    color = _GetGeneric()
    color_power = _GetGeneric()

    def __len__(self):
        return len(self.devices)

    def __iter__(self):
        return iter(self.devices)

    def __getitem__(self, idx):
        return self.devices[idx]

    def __str__(self):
        start_end = f'\n{80 * "="}\n'
        device_str = '\n'.join(map(str, self))
        name_str = f' {self.name!r}' if self.name else ''
        return f'{start_end}{type(self).__name__}{name_str} ({len(self.devices)} lights):\n{device_str}{start_end}'

    def __add__(self, other):
        if isinstance(other, Device):
            return Group(self.devices + [other])
        if isinstance(other, Iterable):
            return Group(chain(self, other))
        return NotImplemented

    def __iadd__(self, other):
        g = self + other
        self.devices[:] = g.devices
        return self


class LightGroup(Group):

    def __init__(self, lights: List[Light]):
        super().__init__(lights)
