# coding=utf-8
# multizonelight.py

import math
import os

from .light import Light
from .msgtypes import MultiZoneGetColorZones, MultiZoneSetColorZones, MultiZoneStateMultiZone, MultiZoneStateZone
from .colors import Color


class MultiZoneLight(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        super(MultiZoneLight, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)

    # 0 indexed, NOT inclusive, works like python list indices
    def get_color_zones(self, start=None, end=None):
        response = self.req_with_resp(MultiZoneGetColorZones, [MultiZoneStateZone, MultiZoneStateMultiZone], {"start_index":0, "end_index":255})
        total_zones = response.count
        # validate indices
        if start is not None and end is not None:
            # automatically truncate if the end is too large
            if end > total_zones:
                end = total_zones
            if start >= total_zones:
                raise ValueError("In the function get_color_zones, starting index is greater than the total available zones (provided start = {}, end = {} for a device with {} total zones).".format(start, end, total_zones))
            if end <= start:
                raise ValueError("In the function get_color_zones, end must be greater than start (provided start = {}, end = {}).".format(start, end, total_zones))
        if (start is not None and end is None) or (start is None and end is not None):
            raise ValueError("In the function get_color_zones, start and end indices must both be provided, or neither provided.")

        # get all zones
        all_zones = []
        for i in range(total_zones):
            all_zones.append(None)
        for i in range(int(math.ceil(total_zones/8.0))):
            response = self.req_with_resp(MultiZoneGetColorZones, [MultiZoneStateZone, MultiZoneStateMultiZone], {"start_index":0+(i*8), "end_index":7+(i*8)})
            first_included_zone = response.index
            if first_included_zone + 8 > total_zones:
                last_included_zone = total_zones-1
                last_index = last_included_zone - first_included_zone
            else:
                last_included_zone = first_included_zone + 7
                last_index = 8
            all_zones[first_included_zone:last_included_zone+1] = response.color[:last_index+1]
        self.color = all_zones

        if start is not None and end is not None:
            self.color = all_zones[start:end]

        return self.color

    def set_zone_color(self, start_index, end_index, color: Color, duration=0, rapid=False, apply=1):
        payload = dict(start_index=start_index, end_index=end_index, color=color, duration=duration, apply=apply)
        self._send_set_message(MultiZoneSetColorZones, payload, rapid=rapid)

    # Sets colors for all zones given a list of HSVK colors
    def set_zone_colors(self, colors, duration=0, rapid=False):
        for (i, color) in enumerate(colors):
            apply = 0
            if i == len(colors)-1:
                apply = 1
            self.set_zone_color(i, i+1, color, duration, rapid, apply)
