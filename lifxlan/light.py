# coding=utf-8
# light.py
# Author: Meghan Clark

import os
from typing import Callable, Tuple

from .settings import Color, unknown, ColorPower

from .device import Device
from .errors import WorkflowException
from .msgtypes import LightGet, LightGetInfrared, LightGetPower, \
    LightSetColor, LightSetInfrared, LightSetPower, LightSetWaveform, \
    LightState, LightStateInfrared, LightStatePower
from .utils import WaitPool

RED = Color(65535, 65535, 65535, 3500)
ORANGE = Color(6500, 65535, 65535, 3500)
YELLOW = Color(9000, 65535, 65535, 3500)
GREEN = Color(16173, 65535, 65535, 3500)
CYAN = Color(29814, 65535, 65535, 3500)
BLUE = Color(43634, 65535, 65535, 3500)
PURPLE = Color(50486, 65535, 65535, 3500)
PINK = Color(58275, 65535, 47142, 3500)
WHITE = Color(58275, 0, 65535, 5500)
COLD_WHITE = Color(58275, 0, 65535, 9000)
WARM_WHITE = Color(58275, 0, 65535, 3200)
GOLD = Color(58275, 0, 65535, 2500)
YALE_BLUE = Color.from_hex(0xF4D92, 9000)
STEELERS_GOLD = Color.from_hex(0xFFB612, 9000)


class Light(Device):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        mac_addr = mac_addr.lower()
        super(Light, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)
        self.color = None
        self.infrared_brightness = None

    ############################################################################
    #                                                                          #
    #                            Light API Methods                             #
    #                                                                          #
    ############################################################################

    @property
    def _refresh_funcs(self) -> Tuple[Callable]:
        return super()._refresh_funcs + (self.get_color,)

    @property
    def power(self):
        return self.power_level

    # GetPower - power level
    def get_power(self):
        try:
            response = self.req_with_resp(LightGetPower, LightStatePower)
            self.power_level = response.power_level
        except WorkflowException as e:
            raise
        return self.power_level

    def set_power(self, power, duration=0, rapid=False):
        print(f'setting power to {power}')
        self._set_power(LightSetPower, power, rapid=rapid, duration=duration)

    # color is [Hue, Saturation, Brightness, Kelvin]
    def set_waveform(self, is_transient, color: Color, period, cycles, duty_cycle, waveform, rapid=False):
        self._send_set_message(LightSetWaveform,
                               dict(transient=is_transient, color=color, period=period, cycles=cycles,
                                    duty_cycle=duty_cycle, waveform=waveform), rapid=rapid)

    def get_color(self) -> Color:
        response = self.req_with_resp(LightGet, LightState)
        self.color = Color(*response.color)
        self.power_level = response.power_level
        self.label = response.label
        return self.color

    def _replace_color(self, color: Color, duration, rapid, **color_kwargs):
        self.set_color(color._replace(**color_kwargs), duration, rapid)

    def set_color(self, color: Color, duration=0, rapid=False):
        print(f'setting color to {color}')
        self._send_set_message(LightSetColor, dict(color=color, duration=duration), rapid=rapid)

    def set_color_power(self, cp: ColorPower, duration=0, rapid=True):
        with WaitPool() as wp:
            if cp.power and cp.color:
                wp.submit(self.set_color, cp.color, duration=duration, rapid=rapid)
            wp.submit(self.set_power, cp.power, duration=duration, rapid=rapid)

    def set_hue(self, hue, duration=0, rapid=False):
        """hue to set; duration in ms"""
        self._replace_color(self.get_color(), duration, rapid, hue=hue)

    def set_saturation(self, saturation, duration=0, rapid=False):
        """saturation to set; duration in ms"""
        self._replace_color(self.get_color(), duration, rapid, saturation=saturation)

    def set_brightness(self, brightness, duration=0, rapid=False):
        """brightness to set; duration in ms"""
        self._replace_color(self.get_color(), duration, rapid, brightness=brightness)

    def set_kelvin(self, kelvin, duration=0, rapid=False):
        """kelvin: color temperature to set; duration in ms"""
        self._replace_color(self.get_color(), duration, rapid, kelvin=kelvin)

    # Infrared get maximum brightness, infrared_brightness
    def get_infrared(self):
        if self.supports_infrared:
            response = self.req_with_resp(LightGetInfrared, LightStateInfrared)
            self.infrared_brightness = response.infrared_brightness
        return self.infrared_brightness

    # Infrared set maximum brightness, infrared_brightness
    def set_infrared(self, infrared_brightness, rapid=False):
        payload = dict(infrared_brightness=infrared_brightness)
        self._send_set_message(LightSetInfrared, payload, rapid=rapid)

    # minimum color temperature supported by light bulb
    def get_min_kelvin(self):
        return self.product_features.get('min_kelvin', unknown)

    # maximum color temperature supported by light bulb
    def get_max_kelvin(self):
        return self.product_features.get('max_kelvin', unknown)

    ############################################################################
    #                                                                          #
    #                            String Formatting                             #
    #                                                                          #
    ############################################################################

    def __str__(self):
        self.refresh()
        indent = "  "
        s = self.device_characteristics_str(indent)
        s += indent + f'Color (HSBK): {self.color}\n'
        s += indent + self.device_firmware_str(indent)
        s += indent + self.device_product_str(indent)
        s += indent + self.device_time_str(indent)
        s += indent + self.device_radio_str(indent)
        return s
