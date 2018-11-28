# import thread
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from functools import partial, wraps
from typing import List

from .light import Light
from .multizonelight import MultiZoneLight
from .settings import Color, Waveform
from .utils import WaitPool, exhaust


def _set_generic(func):
    @wraps(func)
    def wrapper(self: Group, *args, **kwargs):
        with self._wait_pool as wp:
            exhaust(wp.submit(getattr(l, func.__name__, *args, **kwargs) for l in self.color_lights))


class Group(object):

    def __init__(self, devices: List['Device'], verbose=False):
        self.devices = devices
        self.verbose = verbose
        self._pool = ThreadPoolExecutor(30)
        self._wait_pool = WaitPool(self._pool)

    @property
    def multizone_lights(self):
        return [l for l in self.devices if l.supports_multizone]

    @property
    def infrared_lights(self):
        return [l for l in self.devices if l.supports_infrared]

    @property
    def color_lights(self):
        return [l for l in self.devices if l.supports_color]

    @property
    def tilechain_lights(self):
        return [l for l in self.devices if l.supports_chain]

    # @property
    def add_device(self, device_object):
        if device_object not in self.devices:
            self.devices.append(device_object)

    def remove_device(self, device_object):
        with suppress(ValueError):
            self.devices.remove(device_object)

    def remove_device_by_name(self, device_name):
        self.devices[:] = [d for d in self.devices if d.label != device_name]

    def get_device_list(self):
        return self.devices

    def set_power(self, power, duration=0, rapid=False):
        with self._wait_pool as wp:
            wp.map(self.set_power_helper, ((d, power, duration, rapid) for d in self.devices))

    @_set_generic
    def set_waveform(self, is_transient, color: Color, period, cycles, duty_cycle, waveform: Waveform, rapid=False):
        pass

    @staticmethod
    def set_power_helper(device, power, duration, rapid):
        if device.is_light:
            device.set_power(power, duration, rapid)  # Light::set_power(power, [duration], [rapid])
        else:
            device.set_power(power, rapid)  # Device::set_power(power, [rapid])

    def set_color(self, color: Color, duration=0, rapid=False):
        # pre-calculate which devices you'll operate on
        # it'll make the color change look more simultaneous
        kwargs = dict(color=color, duration=duration, rapid=rapid)
        with self._wait_pool as wp:
            exhaust(wp.submit(l.set_color, **kwargs) for l in self.color_lights)

    def set_hue(self, hue, duration=0, rapid=False):
        # pre-calculate which devices to operate on
        kwargs = dict(hue=hue, duration=duration, rapid=rapid)
        with self._wait_pool as wp:
            exhaust(wp.submit(l.set_hue, **kwargs) for l in self.color_lights)

    def set_brightness(self, brightness, duration=0, rapid=False):
        f = partial(Light.set_brightness, brightness=brightness, duration=duration, rapid=rapid)
        with self._wait_pool as wp:
            exhaust(wp.submit(l.set_brightness, **kwargs) for l in self.color_lights)

    def set_saturation(self, saturation, duration=0, rapid=False):
        f = partial(Light.set_saturation, saturation=saturation, duration=duration, rapid=rapid)
        with self._wait_pool as wp:
            wp.map(f, self.color_lights)

    def set_kelvin(self, kelvin, duration=0, rapid=False):
        f = partial(Light.set_kelvin, kelvin=kelvin, duration=duration, rapid=rapid)
        with self._wait_pool as wp:
            wp.map(f, self.color_lights)

    def set_infrared(self, infrared_brightness):
        # pre-calculate which devices to operate on
        f = partial(Light.set_infrared, infrared_brightness=infrared_brightness)
        with self._wait_pool as wp:
            wp.map(f, self.infrared_lights)

    def set_zone_color(self, start, end, color, duration=0, rapid=False, apply=1):
        # pre-calculate which devices to operate on
        f = partial(MultiZoneLight.set_zone_color, start=start, end=end, color=color, duration=duration, rapid=rapid,
                    apply=apply)
        with self._wait_pool as wp:
            wp.map(f, self.multizone_lights)

    def set_zone_colors(self, colors, duration=0, rapid=False):
        # pre-calculate which devices to operate on
        f = partial(MultiZoneLight.set_zone_colors, colors=colors, duration=duration, rapid=rapid)
        with self._wait_pool as wp:
            wp.map(f, self.multizone_lights)

    def __str__(self):
        s = "Group ({}):\n\n".format(len(self.devices))
        for d in self.devices:
            s += str(d) + "\n"
        return s
