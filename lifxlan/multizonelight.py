#multizonelight.py
#Author: Scott Lusebrink

from .light import *
from .device import Device, WorkflowException
from .msgtypes import *
import math

class MultiZoneLight(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=0, verbose=False):
        super(MultiZoneLight, self).__init__(mac_addr, ip_addr)

    # 0 indexed, inclusive
    def get_color_zones(self, start=0, end=255):
        #try:
        response = self.req_with_resp(MultiZoneGetColorZones, [MultiZoneStateZone, MultiZoneStateMultiZone], {"start_index":0, "end_index":255})
        total_zones = response.count
        # automatically truncate if the end is too large
        if end >= total_zones:
            end = total_zones-1
        if start >= total_zones:
            raise ValueError("In the function get_color_zones, starting index is greater than the total available zones (provided start = {}, end = {} for a device with {} total zones).".format(start, end, total_zones))
        if end <= start:
            raise ValueError("In the function get_color_zones, end must be greater than start (provided start = {}, end = {}).".format(start, end, total_zones))

        # get all zones
        if start == 0 and end == 255:
            all_zones = []
            for i in range(int(math.ceil(total_zones / 8.0))):
                response = self.req_with_resp(MultiZoneGetColorZones, [MultiZoneStateZone, MultiZoneStateMultiZone], {"start_index":0+(i*8), "end_index":7+(i*8)})
                all_zones += response.color
            self.color = all_zones[0:total_zones]
        # get specified zone range
        else:
            all_zones = []
            total_requested_zones = end - start + 1
            lower_8_aligned = start - (start % 8)
            upper_8_aligned = end - (end % 8)
            #for i in range(int(math.ceil(upper_8_aligned / 8.0))+1):
            for i in range(((upper_8_aligned - lower_8_aligned) / 8) + 1):
                response = self.req_with_resp(MultiZoneGetColorZones, [MultiZoneStateZone, MultiZoneStateMultiZone], {"start_index":lower_8_aligned+(i*8), "end_index":lower_8_aligned+7+(i*8)})
                all_zones += response.color
            self.color = all_zones[(start % 8):((start % 8)+total_requested_zones)]
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
                raise

    # Sets colors for all zones given a list of HSVK colors
    def set_zone_colors(self, colors, duration=0, rapid=False):
        for (i, color) in enumerate(colors):
            apply = 0
            if i == len(colors)-1:
                apply = 1
            self.set_zone_color(i, i+1, color, duration, rapid, apply)
