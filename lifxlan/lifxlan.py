# coding=utf-8
# lifxlan.py
# Author: Meghan Clark
from concurrent.futures import wait
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, socket, timeout
from time import sleep, time
import os
from typing import List, Optional, Dict

from .settings import Color, PowerSettings
from .device import DEFAULT_ATTEMPTS, DEFAULT_TIMEOUT, UDP_BROADCAST_IP_ADDRS, UDP_BROADCAST_PORT
from .errors import WorkflowException
from .light import Light
from .message import BROADCAST_MAC
from .msgtypes import Acknowledgement, GetService, LightGet, LightGetPower, LightSetColor, LightSetPower, \
    LightSetWaveform, LightState, LightStatePower, StateService
from .multizonelight import MultiZoneLight
from .tilechain import TileChain
from .unpack import unpack_lifx_message
from .group import Group


class LifxLAN:
    def __init__(self, verbose=False):
        self.source_id = os.getpid()
        self.num_devices = 13
        self.devices: List[Light] = []
        self.verbose = verbose
        self._pool = ThreadPoolExecutor(40)
        self.refresh()

    ############################################################################
    #                                                                          #
    #                         LAN (Broadcast) API Methods                      #
    #                                                                          #
    ############################################################################

    @property
    def lights(self) -> List[Light]:
        return [d for d in self.devices if d.is_light]

    def refresh(self):
        """get available devices"""
        futures = []
        self.devices.clear()
        self.num_devices = 10000
        responses = self._broadcast_with_resp(GetService, StateService)
        for r in responses:
            args = r.target_addr, r.ip_addr, r.service, r.port, self.source_id, self.verbose
            with suppress(WorkflowException):
                device = Light(*args)
                if device.is_light:
                    if device.supports_multizone:
                        device = MultiZoneLight(*args)
                    elif device.supports_chain:
                        device = TileChain(*args)
            self.devices.append(device)
            futures.append(self._pool.submit(device.refresh))
        wait(futures)
        self.num_devices = len(self.devices)

    def get_multizone_lights(self):
        return [l for l in self.lights if l.supports_multizone]

    def get_infrared_lights(self):
        return [l for l in self.lights if l.supports_infrared]

    def get_color_lights(self):
        return [l for l in self.lights if l.supports_color]

    def get_tilechain_lights(self):
        return [l for l in self.lights if l.supports_chain]

    def get_device_by_name(self, name):
        device = None
        all_devices = self.devices
        for d in all_devices:
            if d.label == name:
                device = d
        if device is None:  # didn't find it?
            self.refresh()  # update list in case it is out of date
            all_devices = self.devices
            for d in all_devices:  # and try again
                if d.label == name:
                    device = d
        return device

    # takes in list of strings, returns Group of devices
    def get_devices_by_name(self, names):
        devices = []
        all_devices = self.devices
        for d in all_devices:
            if d.label in names:
                devices.append(d)
        if len(devices) != len(names):  # didn't find everything?
            self.refresh()  # update list in case it is out of date
            all_devices = self.devices
            for d in all_devices:  # and try again
                if d.label in names:
                    devices.append(d)
        return Group(devices)

    def get_devices_by_group(self, group):
        devices = []
        all_devices = self.devices
        for d in all_devices:
            if d.group == group:
                devices.append(d)
        return Group(devices)

    def get_devices_by_location(self, location):
        devices = []
        all_devices = self.devices
        for d in all_devices:
            if d.location == location:
                devices.append(d)
        return Group(devices)

    #
    def _get_matched_by_by_addr(self, responses):
        """return gen expr of (light, resp) matched by mac address"""
        if not self.devices:
            self.refresh()
        lights_by_addr = {l.mac_addr: l for l in self.lights}
        responses_by_addr = {r.target_addr: r for r in responses}
        return ((lights_by_addr[addr], responses_by_addr[addr])
                for addr in lights_by_addr.keys() & responses_by_addr.keys())

    def get_power_all_lights(self):
        """return dict of light: power_level"""
        responses = self._broadcast_with_resp(LightGetPower, LightStatePower)
        return {l: r.power_level for l, r in self._get_matched_by_by_addr(responses)}

    def get_color_all_lights(self):
        responses = self._broadcast_with_resp(LightGet, LightState)
        return {l: Color(*r.color) for l, r in self._get_matched_by_by_addr(responses)}

    def set_power_all_lights(self, power_level, duration=0, rapid=False):
        payload = dict(power_level=PowerSettings.validate(power_level), duration=duration)
        self._send_bcast_set_message(LightSetPower, payload, rapid=rapid)

    def set_color_all_lights(self, color: Color, duration=0, rapid=False):
        payload = dict(color=color, duration=duration)
        self._send_bcast_set_message(LightSetColor, payload, rapid=rapid)

    def set_waveform_all_lights(self, is_transient, color, period, cycles, duty_cycle, waveform, rapid=False):
        payload = dict(transient=is_transient, color=color, period=period, cycles=cycles, duty_cycle=duty_cycle,
                       waveform=waveform)
        self._send_bcast_set_message(LightSetWaveform, payload, rapid=rapid)

    ############################################################################
    #                                                                          #
    #                            Workflow Methods                              #
    #                                                                          #
    ############################################################################

    def _send_bcast_set_message(self, msg_type, payload: Optional[Dict] = None, timeout_secs=DEFAULT_TIMEOUT,
                                max_attempts=DEFAULT_ATTEMPTS, *, rapid: bool):
        """handle sending messages either rapidly or not"""
        args = msg_type, payload or {}, timeout_secs
        if rapid:
            self._broadcast_fire_and_forget(*args, num_repeats=max_attempts)
        else:
            self.broadcast_with_ack(*args, max_attempts=max_attempts)

    def _broadcast_fire_and_forget(self, msg_type, payload: Optional[Dict] = None, timeout_secs=DEFAULT_TIMEOUT,
                                   num_repeats=DEFAULT_ATTEMPTS):
        payload = payload or {}
        self.initialize_socket(timeout_secs)
        msg = msg_type(BROADCAST_MAC, self.source_id, seq_num=0, payload=payload, ack_requested=False,
                       response_requested=False)
        sent_msg_count = 0
        sleep_interval = 0.05 if num_repeats > 20 else 0
        while sent_msg_count < num_repeats:
            for ip_addr in UDP_BROADCAST_IP_ADDRS:
                self.sock.sendto(msg.packed_message, (ip_addr, UDP_BROADCAST_PORT))
            if self.verbose:
                print("SEND: " + str(msg))
            sent_msg_count += 1
            sleep(sleep_interval)  # Max num of messages device can handle is 20 per second.
        self.close_socket()

    def _broadcast_with_resp(self, msg_type, response_type, payload: Optional[Dict] = None,
                             timeout_secs=DEFAULT_TIMEOUT,
                             max_attempts=DEFAULT_ATTEMPTS):
        payload = payload or {}
        self.initialize_socket(timeout_secs)
        if response_type == Acknowledgement:
            msg = msg_type(BROADCAST_MAC, self.source_id, seq_num=0, payload=payload, ack_requested=True,
                           response_requested=False)
        else:
            msg = msg_type(BROADCAST_MAC, self.source_id, seq_num=0, payload=payload, ack_requested=False,
                           response_requested=True)
        responses = []
        addr_seen = []
        num_devices_seen = 0
        attempts = 0
        while (self.num_devices is None or num_devices_seen < self.num_devices) and attempts < max_attempts:
            sent = False
            start_time = time()
            timedout = False
            while (self.num_devices is None or num_devices_seen < self.num_devices) and not timedout:
                if not sent:
                    for ip_addr in UDP_BROADCAST_IP_ADDRS:
                        self.sock.sendto(msg.packed_message, (ip_addr, UDP_BROADCAST_PORT))
                    sent = True
                    if self.verbose:
                        print("SEND: " + str(msg))
                try:
                    data, (ip_addr, port) = self.sock.recvfrom(1024)
                    response = unpack_lifx_message(data)
                    response.ip_addr = ip_addr
                    if self.verbose:
                        print("RECV: " + str(response))
                    if type(response) == response_type and response.source_id == self.source_id:
                        if response.target_addr not in addr_seen and response.target_addr != BROADCAST_MAC:
                            addr_seen.append(response.target_addr)
                            num_devices_seen += 1
                            responses.append(response)
                except timeout:
                    pass
                elapsed_time = time() - start_time
                timedout = True if elapsed_time > timeout_secs else False
            attempts += 1
        self.close_socket()
        return responses

    def broadcast_with_ack(self, msg_type, payload={}, timeout_secs=DEFAULT_TIMEOUT + 0.5,
                           max_attempts=DEFAULT_ATTEMPTS):
        self._broadcast_with_resp(msg_type, Acknowledgement, payload, timeout_secs, max_attempts)

    # Not currently implemented, although the LIFX LAN protocol supports this kind of workflow natively
    def broadcast_with_ack_resp(self, msg_type, response_type, payload={}, timeout_secs=DEFAULT_TIMEOUT + 0.5,
                                max_attempts=DEFAULT_ATTEMPTS):
        raise NotImplementedError

    ############################################################################
    #                                                                          #
    #                              Socket Methods                              #
    #                                                                          #
    ############################################################################

    def initialize_socket(self, timeout):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock.settimeout(timeout)
        try:
            self.sock.bind(("", 0))  # allow OS to assign next available source port
        except Exception as err:
            raise WorkflowException("WorkflowException: error {} while trying to open socket".format(str(err)))

    def close_socket(self):
        self.sock.close()


def test():
    pass


if __name__ == "__main__":
    test()
