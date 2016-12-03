#multizonelight.py
#Author: Scott Lusebrink

from light import *
from device import Device, WorkflowException
from msgtypes import *

class MultiZoneLight(Light):
    def __init__(self,light):
        self.light = light
        self.mac_addr = light.mac_addr
        self.source_id = light.source_id
        self.port = light.port
        self.verbose = True
        light.verbose = True
        # Light.__init__(self)


def get_color_zones(self):
    try:
        response = self.light.req_with_resp(LightGetColorZones, LightStateZone)
        self.count = response.count
    except WorkflowException as e:
        print(e)
    return self.count

    # color is [Hue, Saturation, Brightness, Kelvin], duration in ms


def set_zone_color(self, start_index, end_index, color, duration=0, rapid=False, apply=1):
    if len(color) == 4:
        try:
            if rapid:
                self.fire_and_forget(LightSetColorZones,
                                     {"start_index": start_index, "end_index": end_index, "color": color,
                                      "duration": duration, "apply": apply}, num_repeats=5)
            else:
                self.req_with_ack(LightSetColorZones,
                                  {"start_index": start_index, "end_index": end_index, "color": color,
                                   "duration": duration, "apply": apply})
        except WorkflowException as e:
            print(e)

