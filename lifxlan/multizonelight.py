# coding=utf-8
# multizonelight.py

import os
from itertools import count
from typing import List, Tuple, Callable

from .themes import Theme
from .base_api import MultizoneAPI
from .colors import Color, ColorPower, Colors
from .light import Light
from .msgtypes import MultizoneGetColorZones, MultizoneSetColorZones, MultizoneStateMultizone, MultizoneStateZone

rapid_default = True


class MultizoneLight(Light, MultizoneAPI):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        super(MultizoneLight, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)
        self._zones: 'Group'

    @property
    def zones(self) -> 'Group':
        return self._zones

    @zones.setter
    def zones(self, vals: List['Zone']):
        from .group import Group
        self._zones = Group(vals, allow_dupes=True)

    @property
    def _refresh_funcs(self) -> Tuple[Callable]:
        # noinspection PyTypeChecker
        return super()._refresh_funcs + (self._refresh_color_zones,)

    def _refresh_color_zones(self):
        zones = []
        for i in count(step=8):
            response = self.req_with_resp(MultizoneGetColorZones, [MultizoneStateZone, MultizoneStateMultizone],
                                          dict(start_index=i, end_index=255))
            zones.extend(Zone(self, i + ci, Color(*c)) for ci, c in enumerate(response.color))
            if len(zones) >= response.count:
                break
        self.zones = zones

    def set_zone_color(self, color: Color, duration=0, rapid=rapid_default, apply=1, start_index=None, end_index=None):
        start_index = start_index or 0
        end_index = end_index or start_index or 255
        payload = dict(start_index=start_index, end_index=end_index, color=color, duration=duration, apply=apply)
        self._send_set_message(MultizoneSetColorZones, payload, rapid=rapid)

    def set_zone_colors(self, colors: List[Color], duration=0, rapid=False, simultaneous=True):
        apply = 0 if simultaneous else 1
        for (i, color) in enumerate(colors):
            self.set_zone_color(color, duration, rapid, apply=apply, start_index=i, end_index=i + 1)

        if simultaneous:
            self.set_zone_color(Colors.DEFAULT, duration, rapid, apply=2, start_index=0, end_index=0)

    def set_theme(self, theme: Theme, power_on=True, duration=0, rapid=rapid_default):
        self.set_zone_colors(theme.get_colors(len(self.zones)), duration, rapid)


class Zone(MultizoneLight):
    def __init__(self, parent: MultizoneLight, idx, color: Color):
        self.__dict__ = parent.__dict__.copy()
        self.label = f'{self.label}_{idx:03}'
        self.idx = idx
        self.color = color

    def set_color(self, color: Color, duration=0, rapid=rapid_default):
        self.color = color
        self.set_zone_color(color, duration, rapid, start_index=self.idx)

    def set_color_power(self, cp: ColorPower, duration=0, rapid=rapid_default):
        c = cp.color
        if cp.power == 0:
            c = c._replace(brightness=0)
        self.set_color(c, duration, rapid)

    def set_power(self, power, duration=0, rapid=rapid_default):
        self.set_color(self.color._replace(brightness=0), duration, rapid)
