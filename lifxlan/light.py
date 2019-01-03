# coding=utf-8
# light.py
# Author: Meghan Clark
import os
from contextlib import contextmanager
from copy import copy
from typing import Callable, Tuple

from lifxlan.base_api import LightAPI
from .colors import ColorPower, Color, Colors
from .device import Device
from .msgtypes import LightGet, LightGetInfrared, LightSetColor, LightSetInfrared, LightSetPower, LightSetWaveform, \
    LightState, LightStateInfrared
from .settings import unknown, Waveform
from .utils import WaitPool, init_log

log = init_log(__name__)


class Light(Device, LightAPI):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        super(Light, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)
        self.color = None
        self.infrared_brightness = None
        self._wait_pool = WaitPool(2)

    ############################################################################
    #                                                                          #
    #                            Light API Methods                             #
    #                                                                          #
    ############################################################################

    def __hash__(self):
        return super().__hash__() ^ hash(self.color)

    def __eq__(self, other):
        return super().__eq__(other) and self.color == other.color

    def __lt__(self, other: 'Light'):
        return self._sort_key < other._sort_key

    @property
    def _sort_key(self) -> str:
        return f'{self.label}|||{self.product_name}'

    @property
    def _refresh_funcs(self) -> Tuple[Callable]:
        return super()._refresh_funcs + (self._refresh_light_state, self._refresh_infrared)

    @property
    def power(self):
        return self.power_level

    @property
    def color_power(self) -> ColorPower:
        return ColorPower(self.color, self.power)

    def set_waveform(self, waveform: Waveform, color: Color, period_msec, num_cycles,
                     *, skew_ratio=.5, is_transient=True, rapid=False):
        skew_ratio = int(skew_ratio * 2 ** 16 - 2 ** 15)
        payload = dict(transient=is_transient, color=color, period=period_msec, cycles=num_cycles,
                       skew_ratio=skew_ratio, waveform=waveform.value)
        disp = {**payload, 'waveform': waveform}
        log.info(f'setting {self.label!r} waveform to {disp}')
        self._send_set_message(LightSetWaveform, payload, rapid=rapid)

    def _refresh_light_state(self):
        """get and update color, power_level, and label from light"""
        response = self.req_with_resp(LightGet, LightState)
        self.color = Color(*response.color)
        self.power_level = response.power_level
        self.label = response.label

    def _refresh_infrared(self):
        """update infrared_brightness if supported"""
        if self.supports_infrared:
            response = self.req_with_resp(LightGetInfrared, LightStateInfrared)
            self.infrared_brightness = response.infrared_brightness

    def set_color(self, color: Color, duration=0, rapid=False):
        if color:
            color = color.clamped
            log.info(f'setting {self.label!r} color to {color} over {duration} msecs')
            self.color = color
            self._send_set_message(LightSetColor, dict(color=color, duration=duration), rapid=rapid)

    def turn_on(self, duration=0):
        self.set_power(1, duration)

    def turn_off(self, duration=0):
        self.set_power(0, duration)

    def set_power(self, power, duration=0, rapid=False):
        self._set_power(LightSetPower, power, rapid=rapid, duration=duration)

    def set_color_power(self, cp: ColorPower, duration=0, rapid=False):
        """set both color and power at the same time"""
        with self._wait_pool as wp:
            wp.submit(self.set_color, cp.color, duration=duration, rapid=rapid)
            wp.submit(self.set_power, cp.power, duration=duration, rapid=rapid)

    def _replace_color(self, color: Color, duration, rapid, offset=False, **color_kwargs):
        """helper func for setting various Color attributes"""
        if offset:
            color_kwargs = {k: getattr(color, k) + v for k, v in color_kwargs.items()}
        c = Color(*map(int, color._replace(**color_kwargs)))
        self.set_color(c, duration, rapid)

    def set_hue(self, hue, duration=0, rapid=False, offset=False):
        """hue to set; duration in ms"""
        self._replace_color(self.color, duration, rapid, offset, hue=hue)

    def set_saturation(self, saturation, duration=0, rapid=False, offset=False):
        """saturation to set; duration in ms"""
        self._replace_color(self.color, duration, rapid, offset, saturation=saturation)

    def set_brightness(self, brightness, duration=0, rapid=False, offset=False):
        """brightness to set; duration in ms"""
        self._replace_color(self.color, duration, rapid, offset, brightness=brightness)

    def set_kelvin(self, kelvin, duration=0, rapid=False, offset=False):
        """kelvin: color temperature to set; duration in ms"""
        self._replace_color(self.color, duration, rapid, offset, kelvin=kelvin)

    def set_infrared(self, infrared_brightness, rapid=False):
        payload = dict(infrared_brightness=infrared_brightness)
        self._send_set_message(LightSetInfrared, payload, rapid=rapid)

    @property
    def min_kelvin(self):
        return self.product_features.get('min_kelvin', unknown)

    @property
    def max_kelvin(self):
        return self.product_features.get('max_kelvin', unknown)

    @contextmanager
    def reset_to_orig(self, duration=3000):
        """reset light to original color/power settings when done"""
        orig = copy(self)
        try:
            yield
        finally:
            self.reset(orig, duration)

    def reset(self, light: 'Light', duration):
        self.set_color_power(ColorPower(light.color, light.power), duration)

    ############################################################################
    #                                                                          #
    #                            String Formatting                             #
    #                                                                          #
    ############################################################################

    def __str__(self):
        s = f'{self.product_name} ({self.label!r})'
        color = Colors.WHITE if self.power else Colors.SNES_DARK_GREY
        s = color.color_str(s)
        return s

    __repr__ = __str__

    def info_str(self):
        indent = "  "
        s = self.device_characteristics_str(indent)
        s += indent + f'Color (HSBK): {self.color}\n'
        s += indent + self.device_firmware_str(indent)
        s += indent + self.device_product_str(indent)
        s += indent + self.device_time_str(indent)
        s += indent + self.device_radio_str(indent)
        return s
