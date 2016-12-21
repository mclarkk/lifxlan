#multizonelight.py
#Author: Scott Lusebrink

from light import *
from device import Device, WorkflowException
from msgtypes import *

class MultiZoneLight(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=0, verbose=False):
        super(MultiZoneLight, self).__init__(mac_addr, ip_addr)


    # This only gets the first StateMultiZone/StateZone response packet,
    # but there may be several!!!
    # Really need a special MultiZone send/recv function!
    # right now can fake it by making multiple requests with different indices
    def get_color_zones(self, start=0, end=255):
        try:
            response = self.req_with_resp(MultiZoneGetColorZones, MultiZoneStateMultiZone, {"start_index":start, "end_index":end})
            self.color = response.color
        except WorkflowException as e:
            try:
                response = self.req_with_resp(MultiZoneGetColorZones, MultiZoneStateZone, {"start_index":start, "end_index":end})
                self.color = response.color
            except WorkflowException as e:
                print(e)
        return self.color

    def set_zone_color(self, start_index, end_index, color, duration=0, rapid=False, apply=1):
        if len(color) == 4:
            try:
                if rapid:
                    self.fire_and_forget(MultiZoneSetColorZones,
                                         {"start_index": start_index, "end_index": end_index, "color": color,
                                          "duration": duration, "apply": apply}, num_repeats=1)
                else:
                    self.req_with_ack(MultiZoneSetColorZones,
                                      {"start_index": start_index, "end_index": end_index, "color": color,
                                       "duration": duration, "apply": apply})
            except WorkflowException as e:
                print(e)

    # Sets colors for all zones given a list of HSVK colors
    def set_zone_colors(self, colors, duration=0, rapid=False):
        for (i, color) in enumerate(colors):
            apply = 0
            if i == len(colors)-1:
                apply = 1
            self.set_zone_color(i, i+1, color, duration, rapid, apply)
