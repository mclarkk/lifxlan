import os
from contextlib import suppress, contextmanager
from functools import partial, wraps
from itertools import chain, repeat, groupby
from typing import List, Union, Dict, Optional, Iterable, Any

from lifxlan.base_api import LightAPI, MultizoneAPI
from .colors import ColorPower, Color
from .device import Device
from .light import Light
from .msgtypes import GetService, StateService
from .multizonelight import MultizoneLight
from .network import broadcast_with_resp
from .settings import Waveform, TOTAL_NUM_LIGHTS
from .themes import Theme
from .tilechain import TileChain
from .utils import WaitPool, exhaust, timer, init_log

rapid_default = True

log = init_log(__name__)


def _call_on_lights(func=None, *, func_name_override=None, light_type='color_lights'):
    """
    call the wrapped `func.__name__` on all lights in the given
    `light_type` argument.
    essentially acts as a pass-through to the underlying light objects themselves

    changing `light_type` in the decorator call will allow you to
    forward calls to multizone and tile light types
    """
    if func is None:
        return partial(_call_on_lights, light_type=light_type, func_name_override=func_name_override)
    func_name = func_name_override or func.__name__

    @wraps(func)
    def wrapper(self: 'Group', *args, **kwargs):
        with self._wait_pool as wp:
            exhaust(wp.submit(getattr(l, func_name), *args, **kwargs) for l in getattr(self, light_type))
        return self._wait_pool.futures

    return wrapper


LightAttrDict = Dict[Light, Any]


class _GetFromLights:
    """
    descriptor

    based on member name and light type, create a dictionary of {Light: attr}
    """

    def __set_name__(self, owner, name):
        self.name = name

    def __init__(self, light_type='color_lights'):
        self.light_type = light_type

    def __get__(self, instance, owner) -> LightAttrDict:
        if not instance:
            return self

        return {d: getattr(d, self.name) for d in getattr(instance, self.light_type)}


class Group(LightAPI, MultizoneAPI):
    """
    this is the workhorse of the whole operation

    everything can be done through `Groups`. you will use this all the time
    """

    def __init__(self, devices: Iterable[Device], name: Optional[str] = None):
        self.devices = devices
        self.name = name or ''
        self._wait_pool = WaitPool(TOTAL_NUM_LIGHTS)

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, devices):
        self._devices = sorted(set(devices))

    def refresh(self):
        with self._wait_pool as wp:
            futures = {d: wp.submit(d.refresh) for d in self.devices}

        for d, fut in futures.items():
            if not fut.result():
                print(f'ERROR with device with name, mac addr {d.label, d.mac_addr}, '
                      f'removing from group. result: {fut.result()}')
                self.remove_device(d)

    # ==================================================================================================================
    # GROUP PROPERTIES
    # ==================================================================================================================

    # noinspection PyTypeChecker
    @property
    def lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.is_light)

    # noinspection PyTypeChecker
    @property
    def color_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_color)

    # noinspection PyTypeChecker
    @property
    def multizone_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_multizone)

    # noinspection PyTypeChecker
    @property
    def infrared_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_infrared)

    # noinspection PyTypeChecker
    @property
    def tilechain_lights(self) -> 'LightGroup':
        return LightGroup(l for l in self.devices if l.supports_chain)

    @property
    def on_lights(self) -> 'Group':
        """group of lights that are currently on"""
        return Group((l for l, p in self.power.items() if p), 'ON')

    @property
    def off_lights(self) -> 'Group':
        """group of lights that are currently off"""
        return Group((l for l, p in self.power.items() if not p), 'OFF')

    # ==================================================================================================================
    # ALTER GROUP IN MEMORY
    # ==================================================================================================================

    def add_device(self, device_object):
        if device_object not in self.devices:
            self.devices.append(device_object)

    def remove_device(self, device_object):
        with suppress(ValueError):
            self.devices.remove(device_object)

    def remove_device_by_name(self, device_name):
        self.devices[:] = [d for d in self.devices if d.label != device_name]

    # ==================================================================================================================
    # SET LIGHT VALUES IN GROUP
    # ==================================================================================================================

    def set_power(self, power: Union[int, LightAttrDict], duration=0, rapid=rapid_default):
        devices, powers = self.devices, repeat(power)
        if isinstance(power, dict):
            devices, powers = zip(*power.items())

        with self._wait_pool as wp:
            exhaust(wp.submit(self._set_power_helper, d, p, duration, rapid) for d, p in zip(devices, powers))

    @staticmethod
    def _set_power_helper(device, power, duration, rapid):
        if device.is_light:
            device.set_power(power, duration, rapid)
        else:
            device.set_power(power, rapid)

    @_call_on_lights
    def set_waveform(self, waveform: Waveform, color: Color, period_msec, num_cycles,
                     *, skew_ratio=.5, is_transient=True, rapid=False):
        """set waveform on color lights"""

    @_call_on_lights
    def set_color(self, color: Color, duration=0, rapid=rapid_default):
        """set color on color lights"""

    def set_color_power(self, cp: Union[ColorPower, Dict[Light, ColorPower]],
                        duration=0, rapid=True):
        """set color and power on color lights"""
        if isinstance(cp, ColorPower):
            return self._set_color_power(cp, duration, rapid)

        with self._wait_pool as wp:
            exhaust(wp.submit(l.set_color_power, _cp, duration, rapid) for l, _cp in cp.items())

    @_call_on_lights(func_name_override='set_color_power')
    def _set_color_power(self, cp: ColorPower, duration=0, rapid=True):
        """set color and power on color lights"""

    @_call_on_lights
    def set_hue(self, hue, duration=0, rapid=rapid_default, offset=False):
        """set hue on color lights"""

    @_call_on_lights
    def set_brightness(self, brightness, duration=0, rapid=rapid_default, offset=False):
        """set brightness on color lights"""

    @_call_on_lights
    def set_saturation(self, saturation, duration=0, rapid=rapid_default, offset=False):
        """set saturation on color lights"""

    @_call_on_lights
    def set_kelvin(self, kelvin, duration=0, rapid=rapid_default, offset=False):
        """set kelvin on color lights"""

    @_call_on_lights
    def set_infrared(self, infrared_brightness):
        """set infrared on color lights"""

    @_call_on_lights(light_type='multizone_lights')
    def set_zone_color(self, start, end, color, duration=0, rapid=rapid_default, apply=1):
        """set zone color on multizone lights"""

    @_call_on_lights(light_type='multizone_lights')
    def set_zone_colors(self, colors, duration=0, rapid=rapid_default):
        """set zone colors on multizone lights"""

    def set_theme(self, theme: Theme, power_on=True, duration=0, rapid=True):
        colors = theme.get_colors(len(self))
        with self._wait_pool as wp:
            exhaust(
                wp.submit(l.set_color_power, ColorPower(c, power_on), duration, rapid) for l, c in zip(self, colors))

    @_call_on_lights
    def turn_on(self, duration=0):
        """turn on lights"""

    @_call_on_lights
    def turn_off(self, duration=0):
        """turn off lights"""

    # ==================================================================================================================
    # GET SETTINGS FROM LIGHTS (reads currently stored values)
    # ==================================================================================================================
    power = _GetFromLights('devices')
    label = _GetFromLights('lights')
    color = _GetFromLights()
    color_power = _GetFromLights()

    # ==================================================================================================================
    # REFRESH SETTINGS FROM LIGHTS (calls out to lights)
    # ==================================================================================================================
    @timer
    @_call_on_lights(func_name_override='_refresh_light_state', light_type='devices')
    def refresh_power(self):
        """refresh all lights' power"""

    @timer
    @_call_on_lights(func_name_override='_refresh_light_state', light_type='color_lights')
    def refresh_color(self):
        """refresh all lights' color"""

    # ==================================================================================================================
    # ACCESS DEVICES MORE EASILY
    # ==================================================================================================================
    def get_device_by_name(self, name) -> Device:
        return next((d for d in self.devices if d.label == name), None)

    def get_devices_by_name(self, names) -> 'Group':
        return Group(d for d in self.devices if d.label in set(names))

    def get_devices_by_group(self, group) -> 'Group':
        return Group(d for d in self.devices if d.group == group)

    def get_devices_by_location(self, location) -> 'Group':
        return Group(d for d in self.devices if d.location == location)

    def auto_group(self) -> Dict[str, 'Group']:
        """group lights together by labels"""

        def key(d):
            split_names = d.label.split()
            return split_names[0] if len(split_names) == 1 else '_'.join(split_names[:-1])

        devices = sorted(self.devices, key=key)
        return {k: Group(v, k) for k, v in groupby(devices, key)}

    @contextmanager
    def reset_to_orig(self, duration=3000, *, orig_override=None):
        """reset group color/power per light to original settings on with block exit"""
        cur_light_state = orig_override
        if not cur_light_state:
            cur_light_state = {l: ColorPower(l.color, l.power) for l in self.devices}
        try:
            yield cur_light_state
        finally:
            self.set_color_power(cur_light_state, duration=duration, rapid=False)

    # ==================================================================================================================
    # MAKE GROUP PYTHONIC
    # ==================================================================================================================
    def __len__(self):
        return len(self.devices)

    def __iter__(self):
        return iter(self.devices)

    def __getitem__(self, idx_or_name) -> 'Group':
        """get light by idx if int, by name otherwise, else try to grab from auto_group"""
        if isinstance(idx_or_name, int):
            return self.devices[idx_or_name]
        res = self.get_device_by_name(idx_or_name)
        if res:
            return Group([res])
        return self.auto_group()[idx_or_name]

    def __str__(self):
        start_end = f'\n{80 * "="}\n'
        device_str = '\n'.join(map(str, self))
        name_str = f' {self.name!r}' if self.name else ''
        return f'{start_end}{type(self).__name__}{name_str} ({len(self.devices)} lights):\n{device_str}{start_end}'

    def __add__(self, other):
        if isinstance(other, Device):
            return Group(self.devices + [other])
        if isinstance(other, Iterable):
            return Group(chain(self, other))
        return NotImplemented

    def __iadd__(self, other):
        g = self + other
        self.devices = g.devices
        return self


class LightGroup(Group):

    def __init__(self, lights: List[Light]):
        super().__init__(lights)


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


class LifxLAN(Group):
    """
    represent all the lights on the lan

    it's a special group that has the ability to query all lights on the network
    use this as the interface into all your lights, then use `Group's` api to play
    around with the lights as groups
    """

    @_populate
    def __init__(self, name: Optional[str] = None, verbose=False):
        self.source_id = os.getpid()
        self._devices_by_mac_addr: Dict[str, Device] = {}
        self._verbose = verbose
        self._wait_pool = WaitPool(40)
        self._wait_pool.dispatch(self._check_for_new_lights)
        self.name = name or ''

    ############################################################################
    #                                                                          #
    #                         LAN (Broadcast) API Methods                      #
    #                                                                          #
    ############################################################################

    @timer
    def populate_devices(self, reset=False, total_num_lights=TOTAL_NUM_LIGHTS):
        """populate available devices"""
        log.info('populating devices')

        if reset:
            self._devices_by_mac_addr.clear()

        responses = broadcast_with_resp(GetService, StateService, self.source_id, total_num_lights=total_num_lights)
        for device in map(self._proc_device_response, responses):
            self._devices_by_mac_addr[device.mac_addr] = device
        self.devices = self._devices_by_mac_addr.values()
        self.name = self.name or 'ALL'
        self.refresh()
        self.devices = self.devices  # force re-sorting via property after refresh

    def _proc_device_response(self, r):
        args = r.target_addr, r.ip_addr, r.service, r.port, self.source_id, self._verbose
        device = Light(*args)
        if device.is_light:
            if device.supports_multizone:
                device = MultizoneLight(*args)
            elif device.supports_chain:
                device = TileChain(*args)
        return device

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
                log.warn(msg)
            else:
                log.info('no new lights found')
        except Exception as e:
            log.error(f'error in _check_for_new_lights: {e!r}')
            raise e
