# light.py
# Author: Meghan Clark

from device import Device, WorkflowException
from msgtypes import *

RED = [62978, 65535, 65535, 3500]
ORANGE = [5525, 65535, 65535, 3500]
YELLOW = [7615, 65535, 65535, 3500]
GREEN = [16173, 65535, 65535, 3500]
CYAN = [29814, 65535, 65535, 3500]
BLUE = [43634, 65535, 65535, 3500]
PURPLE = [50486, 65535, 65535, 3500]
PINK = [58275, 65535, 47142, 3500]
WHITE = [58275, 0, 65535, 5500]
COLD_WHTE = [58275, 0, 65535, 9000]
WARM_WHITE = [58275, 0, 65535, 3200]
GOLD = [58275, 0, 65535, 2500]

class Light(Device):
    def __init__(self, mac_addr, service, port, source_id, ip_addr, verbose=False):
        super(Light, self).__init__(mac_addr, service, port, source_id, ip_addr, verbose)
        self.color = None

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
            print(e)
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
                print("{} is not a valid power level.".format(power))
        except WorkflowException as e:
            print(e)

    # color is [Hue, Saturation, Brightness, Kelvin], duration in ms
    def set_color(self, color, duration=0, rapid=False):
        if len(color) == 4:
            try:
                if rapid:
                    self.fire_and_forget(LightSetColor, {"color": color, "duration": duration}, num_repeats=5)
                else:
                    self.req_with_ack(LightSetColor, {"color": color, "duration": duration})
            except WorkflowException as e:
                print(e)

    # LightGet, color, power_level, label
    def get_color(self):
        try:
            response = self.req_with_resp(LightGet, LightState)
            self.color = response.color
            self.power_level = response.power_level
            self.label = response.label
        except WorkflowException as e:
            print(e)
        return self.color

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