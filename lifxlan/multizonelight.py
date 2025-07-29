# coding=utf-8
# multizonelight.py

import math
import random

from .device import WorkflowException
from .errors import InvalidParameterException
from .light import Light
from .msgtypes import MultiZoneGetColorZones, MultiZoneSetColorZones, MultiZoneStateMultiZone, MultiZoneStateZone, GetMultiZoneEffect, SetMultiZoneEffect, StateMultiZoneEffect, MultiZoneGetExtendedColorZones, MultiZoneSetExtendedColorZones, MultiZoneStateExtendedColorZones


class MultiZoneLight(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=random.randrange(2, 1 << 32), verbose=False):
        super(MultiZoneLight, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)

    # 0 indexed, NOT inclusive, works like python list indices
    def get_color_zones(self, start=None, end=None):
        response = self.req_with_resp(MultiZoneGetColorZones, [MultiZoneStateZone, MultiZoneStateMultiZone], {"start_index":0, "end_index":255})
        total_zones = response.count
        # validate indices
        if start != None and end != None:
            # automatically truncate if the end is too large
            if end > total_zones:
                end = total_zones
            if start >= total_zones:
                raise ValueError("In the function get_color_zones, starting index is greater than the total available zones (provided start = {}, end = {} for a device with {} total zones).".format(start, end, total_zones))
            if end <= start:
                raise ValueError("In the function get_color_zones, end must be greater than start (provided start = {}, end = {}).".format(start, end, total_zones))
        if (start != None and end == None) or (start == None and end != None):
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

        if start != None and end != None:
            self.color = all_zones[start:end]

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

    # Uses new protocol for extended color zones, 0-indexed, end is exclusive.
    def extended_get_color_zones(self, start=None, end=None):
        responses = self.req_with_multiple_resp(MultiZoneGetExtendedColorZones, [MultiZoneStateExtendedColorZones])
        colors = []

        if (start != None and end == None) or (start == None and end != None):
            raise ValueError("In the function extended_get_color_zones, start and end indices must both be provided, or neither provided.")
        elif start is not None and end is not None:
            if end < start:
                raise ValueError("In the function extended_get_color_zones, end must be greater than start (provided start = {}, end = {}).".format(start, end))

        for response in responses:
            for i in range(response.index, response.index + response.cCount):
                if (start is None and end is None) or (i >= start and i < end):
                    if i < response.count:
                        colors.append(response.colors[i - response.index])
                    else:
                        raise WorkflowException("extended_get_color_zones response exceeds total count: segment index={}, color count={}, zone count={}".format(response.index, response.cCount, response.count))
                        break

        return colors   

    def extended_set_zone_color(self, colors, index=0, duration=0, rapid=False, apply=1):
        if not isinstance(colors, list):
            colors = [colors]
        if all((isinstance(color, tuple) or isinstance(color, list)) and len(color) == 4 for color in colors):
            requests = int(math.ceil(len(colors)/82.0))
            try:
                for i in range(requests):
                    start_index = i * 82
                    applyFlag = 1 if (i == requests - 1) and (apply == 1) else 0
                    segment_colors = colors[start_index:start_index + 82]

                    if rapid:
                        self.fire_and_forget(MultiZoneSetExtendedColorZones,
                                             {"index": start_index + index, "colors": segment_colors,
                                              "duration": duration, "count" : len(segment_colors), "apply": applyFlag}, num_repeats=1)
                    else:
                        self.req_with_ack(MultiZoneSetExtendedColorZones, {"index": start_index + index, "colors": segment_colors,
                                                                           "duration": duration, "apply": applyFlag, "count": len(segment_colors)})
            except WorkflowException as e:
                raise

    def get_multizone_effect(self):
        response = self.req_with_resp(GetMultiZoneEffect, StateMultiZoneEffect)
        effect = {"instanceid": response.instanceid,
                  "type": response.effect_type,
                  "speed": response.speed,
                  "duration": response.duration,
                  "parameters": response.parameters}
        return effect

    def set_multizone_effect(self, effect_type=0, speed=0, duration=0, instanceid=0, parameters=[], rapid=False):
        if len(parameters)>8:
            raise InvalidParameterException("Maximum parameters size is 8, {} given.".format(len(parameters)))

        if len(parameters) < 8:
            for i in range(len(parameters), 8):
                parameters.append(0)

        payload = {"instanceid": instanceid,
                   "type": effect_type,
                   "reserved1": 0,
                   "speed": speed,
                   "duration": duration,
                   "reserved2": 0,
                   "reserved3": 0,
                   "parameters": parameters}
        if not rapid:
            self.req_with_ack(SetMultiZoneEffect, payload)
        else:
            self.fire_and_forget(SetMultiZoneEffect, payload, num_repeats=1)
