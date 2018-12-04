# coding=utf-8
# lifxlan.py
# Author: Meghan Clark
import os
from contextlib import suppress
from functools import wraps
from itertools import groupby
from typing import Dict

from .device import Device
from .errors import WorkflowException
from .group import Group
from .light import Light
from .msgtypes import GetService, StateService
from .multizonelight import MultiZoneLight
from .network import broadcast_with_resp
from .settings import TOTAL_NUM_LIGHTS
from .tilechain import TileChain
from .utils import timer, WaitPool


def _populate(func):
    """used to ensure that `populate_devices` occurs after LifxLAN.__init__"""
    @wraps(func)
    def wrapper(self: 'LifxLAN', *args, **kwargs):
        res = func(self, *args, **kwargs)
        try:
            self.populate_devices()
        finally:
            return res

    return wrapper


class _FromGroup:
    """
    forward attribute access to `_group` based on member name

    in other words, get the attribute from the group
    """

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance: 'LifxLAN', owner):
        if not instance:
            return self
        return getattr(instance._group, self.name)


class LifxLAN:
    @_populate
    def __init__(self, verbose=False):
        self.source_id = os.getpid()
        self._devices_by_mac_addr: Dict[str, Device] = {}
        self._verbose = verbose
        self._wait_pool = WaitPool(40)
        self._group: Group = None
        self._wait_pool.dispatch(self._check_for_new_lights)

    ############################################################################
    #                                                                          #
    #                         LAN (Broadcast) API Methods                      #
    #                                                                          #
    ############################################################################

    # ==================================================================================================================
    # accessors to lights from group
    # ==================================================================================================================
    devices = _FromGroup()
    lights = _FromGroup()
    multizone_lights = _FromGroup()
    infrared_lights = _FromGroup()
    color_lights = _FromGroup()
    tilechain_lights = _FromGroup()

    # ==================================================================================================================
    # accessors to light settings
    # ==================================================================================================================
    power = _FromGroup()
    color = _FromGroup()
    color_power = _FromGroup()

    @property
    def on_lights(self) -> Group:
        """group of lights that are currently on"""
        return Group((l for l, p in self.power.items() if p), 'ON')

    @property
    def off_lights(self):
        """group of lights that are currently off"""
        return Group((l for l, p in self.power.items() if not p), 'OFF')

    @timer
    def populate_devices(self, reset=False, total_num_lights=TOTAL_NUM_LIGHTS):
        """populate available devices"""

        if reset:
            self._devices_by_mac_addr.clear()

        responses = broadcast_with_resp(GetService, StateService, self.source_id, total_num_lights=total_num_lights)
        for device in map(self._proc_device_response, responses):
            self._devices_by_mac_addr[device.mac_addr] = device
        self._group = Group(self._devices_by_mac_addr.values())
        self.refresh()

    @timer
    def refresh(self):
        """refresh stats on available devices"""
        self._group.refresh()

    def _proc_device_response(self, r):
        args = r.target_addr, r.ip_addr, r.service, r.port, self.source_id, self._verbose
        with suppress(WorkflowException):
            device = Light(*args)
            if device.is_light:
                if device.supports_multizone:
                    device = MultiZoneLight(*args)
                elif device.supports_chain:
                    device = TileChain(*args)
        return device

    def get_device_by_name(self, name) -> Device:
        return next((d for d in self.devices if d.label == name), None)

    def get_devices_by_name(self, names) -> Group:
        return Group(d for d in self.devices if d.label in set(names))

    def get_devices_by_group(self, group):
        return Group(d for d in self.devices if d.group == group)

    def get_devices_by_location(self, location):
        return Group(d for d in self.devices if d.location == location)

    def auto_group(self) -> Dict[str, Group]:
        def key(d):
            split_names = d.label.split()
            return split_names[0] if len(split_names) == 1 else '_'.join(split_names[:-1])

        devices = sorted(self.devices, key=key)
        return {k: Group(v, k) for k, v in groupby(devices, key)}

    @timer
    def _check_for_new_lights(self):
        """
        run a check in the background and warn if we find new lights
        that we haven't accounted for in `TOTAL_NUM_LIGHTS`
        """
        try:
            num_resps = len(broadcast_with_resp(GetService, StateService, self.source_id, total_num_lights=10000))
            if num_resps != TOTAL_NUM_LIGHTS:
                import warnings
                msg = f'WARNING: found {num_resps} devices, but TOTAL_NUM_LIGHTS is set to {TOTAL_NUM_LIGHTS}'
                warnings.warn(ResourceWarning(msg))
                print(msg)
            else:
                print('no new lights found')
        except Exception as e:
            print(f'error in _check_for_new_lights: {e!r}')
            raise e


def test():
    pass


if __name__ == "__main__":
    test()
