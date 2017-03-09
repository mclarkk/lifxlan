# light.py
# Author: Meghan Clark

from .device import Device
from .msgtypes import *
from .errors import WorkflowException, InvalidParameterException

RED = [65535, 65535, 65535, 3500]
ORANGE = [5525, 65535, 65535, 3500]
YELLOW = [7000, 65535, 65535, 3500]
GREEN = [16173, 65535, 65535, 3500]
CYAN = [29814, 65535, 65535, 3500]
BLUE = [43634, 65535, 65535, 3500]
PURPLE = [50486, 65535, 65535, 3500]
PINK = [58275, 65535, 47142, 3500]
WHITE = [58275, 0, 65535, 5500]
COLD_WHITE = [58275, 0, 65535, 9000]
WARM_WHITE = [58275, 0, 65535, 3200]
GOLD = [58275, 0, 65535, 2500]

class Light(Device):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=0, verbose=False):
        mac_addr = mac_addr.lower()
        super(Light, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)
        self.color = None
        self.infrared_brightness = None

    ############################################################################
    #                                                                          #
    #                            Light API Methods                             #
    #                                                                          #
    ############################################################################

    # GetPower - power level
    def get_power(self):
        try:
            response = self.req_with_resp(LightGetPower, LightStatePower)
            self.power_level = response.power_level
        except WorkflowException as e:
            raise
        return self.power_level

    def set_power(self, power, duration=0, rapid=False):
        on = [True, 1, "on", 65535]
        off = [False, 0, "off"]
        try:
            if power in on and not rapid:
                self.req_with_ack(LightSetPower, {"power_level": 65535, "duration": duration})
            elif power in on and rapid:
                self.fire_and_forget(LightSetPower, {"power_level": 65535, "duration": duration}, num_repeats=5)
            elif power in off and not rapid:
                self.req_with_ack(LightSetPower, {"power_level": 0, "duration": duration})
            elif power in off and rapid:
                self.fire_and_forget(LightSetPower, {"power_level": 0, "duration": duration}, num_repeats=5)
            else:
                raise InvalidParameterException("{} is not a valid power level.".format(power))
        except WorkflowException as e:
            raise

    # color is [Hue, Saturation, Brightness, Kelvin]
    def set_waveform(self, is_transient, color, period, cycles, duty_cycle, waveform, rapid=False):
        if len(color) == 4:
            try:
                if rapid:
                    self.fire_and_forget(LightSetWaveform, {"transient": is_transient, "color": color, "period": period, "cycles": cycles, "duty_cycle": duty_cycle, "waveform": waveform}, num_repeats=5)
                else:
                    self.req_with_ack(LightSetWaveform, {"transient": is_transient, "color": color, "period": period, "cycles": cycles, "duty_cycle": duty_cycle, "waveform": waveform})
            except WorkflowException as e:
                raise

    # color is [Hue, Saturation, Brightness, Kelvin], duration in ms
    def set_color(self, color, duration=0, rapid=False):
        if len(color) == 4:
            try:
                if rapid:
                    self.fire_and_forget(LightSetColor, {"color": color, "duration": duration}, num_repeats=5)
                else:
                    self.req_with_ack(LightSetColor, {"color": color, "duration": duration})
            except WorkflowException as e:
                raise

    def get_color(self):
        try:
            response = self.req_with_resp(LightGet, LightState)
            self.color = response.color
            self.power_level = response.power_level
            self.label = response.label
        except WorkflowException as e:
            raise
        return self.color

    # hue in range [0 - 65535]
    def set_hue(self, hue, duration=0, rapid=False):
        """ hue to set
            duration in ms"""
        color = self.get_color()
        color2 = (hue, color[1], color[2], color[3])
        try:
            if rapid:
                self.fire_and_forget(LightSetColor, {"color": color2, "duration": duration}, num_repeats=5)
            else:
                self.req_with_ack(LightSetColor, {"color": color2, "duration": duration})
        except WorkflowException as e:
            raise

    # saturation in range [0 - 65535]
    def set_saturation(self, saturation, duration=0, rapid=False):
        """ saturation to set
            duration in ms"""
        color = self.get_color()
        color2 = (color[0], saturation, color[2], color[3])
        try:
            if rapid:
                self.fire_and_forget(LightSetColor, {"color": color2, "duration": duration}, num_repeats=5)
            else:
                self.req_with_ack(LightSetColor, {"color": color2, "duration": duration})
        except WorkflowException as e:
            raise

    # brightness in range [0 - 65535]
    def set_brightness(self, brightness, duration=0, rapid=False):
        """ brightness to set
            duration in ms"""
        color = self.get_color()
        color2 = (color[0], color[1], brightness, color[3])
        try:
            if rapid:
                self.fire_and_forget(LightSetColor, {"color": color2, "duration": duration}, num_repeats=5)
            else:
                self.req_with_ack(LightSetColor, {"color": color2, "duration": duration})
        except WorkflowException as e:
            raise

    # kelvin in range [2500 - 9000]
    def set_colortemp(self, kelvin, duration=0, rapid=False):
        """ kelvin: color temperature to set
            duration in ms"""
        color = self.get_color()
        color2 = (color[0], color[1], color[2], kelvin)
        try:
            if rapid:
                self.fire_and_forget(LightSetColor, {"color": color2, "duration": duration}, num_repeats=5)
            else:
                self.req_with_ack(LightSetColor, {"color": color2, "duration": duration})
        except WorkflowException as e:
            raise

    # Infrared get maximum brightness, infrared_brightness
    def get_infrared(self):
        if self.supports_infrared():
            try:
                response = self.req_with_resp(LightGetInfrared, LightStateInfrared)
                self.infrared_brightness = response.infrared_brightness
            except WorkflowException as e:
                raise
        return self.infrared_brightness

    # Infrared set maximum brightness, infrared_brightness
    def set_infrared(self, infrared_brightness, rapid=False):
        try:
            if rapid:
                self.fire_and_forget(LightSetInfrared, {"infrared_brightness": infrared_brightness}, num_repeats=5)
            else:
                self.req_with_ack(LightSetInfrared, {"infrared_brightness": infrared_brightness})
        except WorkflowException as e:
            raise

    ############################################################################
    #                                                                          #
    #                            String Formatting                             #
    #                                                                          #
    ############################################################################

    def __str__(self):
        self.refresh()
        indent = "  "
        s = self.device_characteristics_str(indent)
        s += indent + "Color (HSBK): {}\n".format(self.get_color())
        s += indent + self.device_firmware_str(indent)
        s += indent + self.device_product_str(indent)
        s += indent + self.device_time_str(indent)
        s += indent + self.device_radio_str(indent)
        return s
