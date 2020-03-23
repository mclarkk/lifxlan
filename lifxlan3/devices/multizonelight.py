# coding=utf-8
# multizonelight.py

import os
from itertools import count
from typing import List, Tuple, Callable

from lifxlan3.utils import init_log, exhaust
from lifxlan3.grid import GridLight, Dir
from lifxlan3.themes import Theme
from lifxlan3.colors import Color, ColorPower, Colors
from .light import Light
from lifxlan3.network.msgtypes import MultizoneGetColorZones, MultizoneSetColorZones, MultizoneStateMultizone, MultizoneStateZone

log = init_log(__name__)
rapid_default = True

_reversed = {'strip 1'}


# TODO: store all multizone lights as groups of their constituent zones - ignore the base light - maybe?

class MultizoneLight(Light):
    """
    represent a light that has multiple zones along one dimension (e.g. lifx z strip)

    the problem is this: each light can be thought of as its own light as well as
    a group of zones, each zone represented as its own light

    i'm not sure how best to solve this duality problem...
    """
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
        self._init_grid()

    def _init_grid(self):
        zone_iter = (reversed if self.label in _reversed else iter)(self.zones)
        cur_gl = GridLight(next(zone_iter).label)
        for next_z in zone_iter:
            next_gl = GridLight(next_z.label)
            cur_gl[Dir.right] = next_gl
            cur_gl = next_gl

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
        """
        set color of individual or slices of zones on the strip

        apply has 3 possible values:
            - 0: queue up changes, but don't yet apply
            - 1: apply immediately
            - 2: apply queued changes
        """
        poss_end_idx = 255 if start_index is None else start_index
        start_index = start_index or 0
        end_index = end_index or poss_end_idx

        log.info(f'setting {self.label!r}[{start_index}:{end_index}] color to {color} over {duration} msecs')
        payload = dict(start_index=start_index, end_index=end_index, color=color, duration=duration, apply=apply)
        self._send_set_message(MultizoneSetColorZones, payload, rapid=rapid)

    def set_zone_colors(self, colors: List[Color], duration=0, rapid=False):
        """set first `len(colors)` zones to `colors`"""
        with self._wait_pool as wp:
            exhaust(wp.submit(self.set_zone_color, color, duration, rapid, apply=0, start_index=i, end_index=i + 1)
                    for (i, color) in enumerate(colors))
        self.set_zone_color(Colors.DEFAULT, 0, False, apply=2)

    def set_theme(self, theme: Theme, power_on=True, duration=0, rapid=rapid_default):
        self.set_zone_colors(theme.get_colors(len(self.zones)), duration, rapid)
        if power_on:
            self.turn_on()


class Zone(MultizoneLight):
    def __init__(self, parent: MultizoneLight, idx, color: Color):
        self.__dict__ = parent.__dict__.copy()
        self.label = f'{self.label}_{idx:02}'
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
