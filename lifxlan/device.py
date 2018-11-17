# coding=utf-8
# device.py
# Author: Meghan Clark
# This file contains a Device object that exposes a high-level API for interacting
# with a LIFX device, and which caches some of the more persistent state attributes
# so that you don't always need to spam the light with packets.
#
# The Device object also provides the low-level workflow functions for sending
# LIFX unicast packets to the specific device. LIFX unicast packets are sent
# via UDP broadcast, but by including the device's MAC other LIFX devices will
# ignore the packet.
#
# Import note: Every time you call a `get` method you are sending packets to the
# real device. If you want to access the last known (cached) value of an attribute
# just access the attribute directly, e.g., mydevice.label instead of mydevice.get_label()
#
# Currently service and port are set during initialization and never updated.
# This may need to change in the future to support multiple (service, port) pairs
# per device, and also to capture in real time when a service is down (port = 0).
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import wait
from datetime import datetime
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, socket, timeout, gethostbyname_ex, \
    gethostname
from time import sleep, time
import platform
import netifaces as ni
from typing import NamedTuple

from .errors import WorkflowException
from .msgtypes import Acknowledgement, GetGroup, GetHostFirmware, GetInfo, GetLabel, GetLocation, GetPower, GetVersion, \
    GetWifiFirmware, GetWifiInfo, SERVICE_IDS, SetLabel, SetPower, StateGroup, StateHostFirmware, StateInfo, StateLabel, \
    StateLocation, StatePower, StateVersion, StateWifiFirmware, StateWifiInfo, str_map
from .message import BROADCAST_MAC
from .products import features_map, product_map, light_products
from .unpack import unpack_lifx_message

DEFAULT_TIMEOUT = 1  # second
DEFAULT_ATTEMPTS = 1

VERBOSE = False


def get_broadcast_addrs():
    broadcast_addrs = []
    for iface in ni.interfaces():
        try:
            ifaddr = ni.ifaddresses(iface)[ni.AF_INET][0]
            if ifaddr['addr'] != '127.0.0.1':
                broadcast_addrs.append(ifaddr['broadcast'])
        except:  # for interfaces that don't support ni.AF_INET
            pass
    return broadcast_addrs


UDP_BROADCAST_IP_ADDRS = get_broadcast_addrs()
UDP_BROADCAST_PORT = 56700


class TimeInfo(NamedTuple):
    time: int
    uptime: int
    downtime: int


class WifiInfo(NamedTuple):
    signal: int
    tx: int
    rx: int


class FirmwareInfo(NamedTuple):
    build_timestamp: int = -1
    version: float = -1.0


class VersionInfo(NamedTuple):
    vendor: str = 'UNKNOWN'
    product: str = 'UNKNOWN'
    version: str = 'UNKNOWN'


class SupportsDesc:
    """return whether or not a certain feature is supported based on the member name"""

    def __set_name__(self, owner, name):
        self.name = name.split('_', 1)[-1]

    def __get__(self, instance, owner):
        if not instance:
            return self
        return instance._supports(self.name)


class Device(object):
    # mac_addr is a string, with the ":" and everything.
    # service is an integer that maps to a service type. See SERVICE_IDS in msgtypes.py
    # source_id is a number unique to this client, will appear in responses to this client
    def __init__(self, mac_addr, ip_addr, service, port, source_id, verbose=False):
        self.verbose = verbose
        self.mac_addr = mac_addr
        self.port = port
        self.service = service
        self.source_id = source_id
        self.ip_addr = ip_addr  # IP addresses can change, though...

        # The following attributes can be set by calling refresh(), but that
        # takes time so it is not done by default during initialization.
        # However, refresh() will be called each time __str__ is called.
        # Printing the device is therefore accurate but expensive.

        self.label = None
        self.location = None
        self.group = None
        self.power_level = None
        self._host_firmware_info = FirmwareInfo()
        self._wifi_firmware_info = FirmwareInfo()
        self._version_info = VersionInfo()

        self._pool = ThreadPoolExecutor(12)

        # For completeness, the following are state attributes of the device
        # that become stale too fast to bother caching in the device object,
        # though they can be accessed directly from the real device using the
        # methods below:

        # wifi signal mw
        # wifi tx bytes
        # wifi rx bytes
        # time
        # uptime
        # downtime

        # The following attributes are used for handling multithreading requests

        self.socket_counter = 0
        self.socket_table = {}

    ###########################################################################
    #                                                                          #
    #                            Device API Methods                            #
    #                                                                          #
    ############################################################################

    @property
    def host_firmware_build_timestamp(self):
        return self._host_firmware_info.build_timestamp

    @property
    def host_firmware_version(self):
        return self._host_firmware_info.version

    @property
    def wifi_firmware_build_timestamp(self):
        return self._wifi_firmware_info.build_timestamp

    @property
    def wifi_firmware_version(self):
        return self._wifi_firmware_info.version

    @property
    def vendor(self):
        return self._version_info.vendor

    @property
    def version(self):
        return self._version_info.version

    @property
    def product(self):
        return self._version_info.product

    @property
    def product_name(self):
        return product_map.get(self._version_info.product, 'UNKNOWN')

    @property
    def product_features(self):
        return features_map.get(self._version_info.product, 'UNKNOWN')

    # update the device's (relatively) persistent attributes
    def refresh(self):
        funcs = (self.get_label,
                 self.get_location,
                 self.get_group,
                 self.get_power,
                 self.get_host_firmware_info,
                 self.get_wifi_firmware_info,
                 self.get_version_info,
                 self.get_product_name,
                 self.get_product_features)
        wait([self._pool.submit(f) for f in funcs])

    def get_label(self):
        response = self.req_with_resp(GetLabel, StateLabel)
        self.label = response.label.encode('utf-8')
        if type(self.label).__name__ == 'bytes':  # Python 3
            self.label = self.label.decode('utf-8')
        return self.label

    def get_location(self):
        response = self.req_with_resp(GetLocation, StateLocation)
        self.location = response.label.encode('utf-8')
        if type(self.location).__name__ == 'bytes':  # Python 3
            self.location = self.location.decode('utf-8')
        return self.location

    def get_group(self):
        response = self.req_with_resp(GetGroup, StateGroup)
        self.group = response.label.encode('utf-8')
        if type(self.group).__name__ == 'bytes':  # Python 3
            self.group = self.group.decode('utf-8')
        return self.group

    def set_label(self, label):
        if len(label) > 32:
            label = label[:32]
        self.req_with_ack(SetLabel, {"label": label})

    def get_power(self):
        response = self.req_with_resp(GetPower, StatePower)
        self.power_level = response.power_level
        return self.power_level

    def set_power(self, power, rapid=False):
        on = [True, 1, "on"]
        off = [False, 0, "off"]
        if power in on and not rapid:
            self.req_with_ack(SetPower, {"power_level": 65535})
        elif power in off and not rapid:
            self.req_with_ack(SetPower, {"power_level": 0})
        elif power in on and rapid:
            self.fire_and_forget(SetPower, {"power_level": 65535})
        elif power in off and rapid:
            self.fire_and_forget(SetPower, {"power_level": 0})

    def get_host_firmware_info(self) -> FirmwareInfo:
        response = self.req_with_resp(GetHostFirmware, StateHostFirmware)
        build = response.build
        version = float(str(str(response.version >> 16) + "." + str(response.version & 0xff)))
        t = self._host_firmware_info = FirmwareInfo(build, version)
        return t

    def get_wifi_info(self) -> WifiInfo:
        response = self.req_with_resp(GetWifiInfo, StateWifiInfo)
        return WifiInfo(response.signal, response.tx, response.rx)

    def get_wifi_firmware_info(self) -> FirmwareInfo:
        response = self.req_with_resp(GetWifiFirmware, StateWifiFirmware)
        build = response.build
        version = float(str(str(response.version >> 16) + "." + str(response.version & 0xff)))
        t = self._wifi_firmware_info = FirmwareInfo(build, version)
        return t

    def get_version_info(self) -> VersionInfo:
        r = self.req_with_resp(GetVersion, StateVersion)
        t = self._version_info = VersionInfo(r.vendor, r.product, r.version)
        return t

    def get_product_name(self):
        self.get_version_info()
        return self.product_name

    def get_product_features(self):
        self.get_version_info()
        return self.product_features

    def get_location_tuple(self):
        response = self.req_with_resp(GetLocation, StateLocation)
        self.location = response.location
        label = response.label
        updated_at = response.updated_at
        return self.location, label, updated_at

    def get_location_label(self):
        self.location, label, updated_at = self.get_location_tuple()
        return label

    def get_location_updated_at(self):
        self.location, label, updated_at = self.get_location_tuple()
        return updated_at

    def get_group_tuple(self):
        try:
            response = self.req_with_resp(GetGroup, StateGroup)
            self.group = response.group
            label = response.label
            updated_at = response.updated_at
        except:
            raise
        return self.group, label, updated_at

    def get_group_label(self):
        self.group, label, updated_at = self.get_group_tuple()
        return label

    def get_group_updated_at(self):
        self.group, label, updated_at = self.get_group_tuple()
        return updated_at

    def get_time_info(self) -> TimeInfo:
        response = self.req_with_resp(GetInfo, StateInfo)
        return TimeInfo(response.time, response.uptime, response.downtime)

    @property
    def is_light(self) -> bool:
        if self.product is None:
            self.get_version_info()
        return self.product in light_products

    def _supports(self, feature: str) -> bool:
        if self.product_features is None:
            self.get_product_features()
        return self.product_features[feature]

    supports_color = SupportsDesc()
    supports_temperature = SupportsDesc()
    supports_multizone = SupportsDesc()
    supports_infrared = SupportsDesc()
    supports_chain = SupportsDesc()

    ############################################################################
    #                                                                          #
    #                            String Formatting                             #
    #                                                                          #
    ############################################################################

    def device_characteristics_str(self, indent):
        s = "{}\n".format(self.label)
        s += indent + "MAC Address: {}\n".format(self.mac_addr)
        s += indent + "IP Address: {}\n".format(self.ip_addr)
        s += indent + "Port: {}\n".format(self.port)
        s += indent + "Service: {}\n".format(SERVICE_IDS[self.service])
        s += indent + "Power: {}\n".format(str_map(self.power_level))
        s += indent + "Location: {}\n".format(self.location)
        s += indent + "Group: {}\n".format(self.group)
        return s

    def device_firmware_str(self, indent):
        host_build_ns = self.host_firmware_build_timestamp
        host_build_s = datetime.utcfromtimestamp(host_build_ns / 1000000000) if host_build_ns is not None else None
        wifi_build_ns = self.wifi_firmware_build_timestamp
        wifi_build_s = datetime.utcfromtimestamp(wifi_build_ns / 1000000000) if wifi_build_ns is not None else None
        s = "Host Firmware Build Timestamp: {} ({} UTC)\n".format(host_build_ns, host_build_s)
        s += indent + "Host Firmware Build Version: {}\n".format(self.host_firmware_version)
        s += indent + "Wifi Firmware Build Timestamp: {} ({} UTC)\n".format(wifi_build_ns, wifi_build_s)
        s += indent + "Wifi Firmware Build Version: {}\n".format(self.wifi_firmware_version)
        return s

    def device_product_str(self, indent):
        s = "Vendor: {}\n".format(self.vendor)
        s += indent + "Product: {} ({})\n".format(self.product, self.product_name)  #### FIX
        s += indent + "Version: {}\n".format(self.version)
        s += indent + "Features: {}\n".format(self.product_features)
        return s

    def device_time_str(self, indent):
        time, uptime, downtime = self.get_time_info()
        time_s = datetime.utcfromtimestamp(time / 1000000000) if time else None
        uptime_s = round(nanosec_to_hours(uptime), 2) if uptime else None
        downtime_s = round(nanosec_to_hours(downtime), 2) if downtime else None
        s = "Current Time: {} ({} UTC)\n".format(time, time_s)
        s += indent + "Uptime (ns): {} ({} hours)\n".format(uptime, uptime_s)
        s += indent + "Last Downtime Duration +/-5s (ns): {} ({} hours)\n".format(downtime, downtime_s)
        return s

    def device_radio_str(self, indent):
        signal, tx, rx = self.get_wifi_info()
        s = "Wifi Signal Strength (mW): {}\n".format(signal)
        s += indent + "Wifi TX (bytes): {}\n".format(tx)
        s += indent + "Wifi RX (bytes): {}\n".format(rx)
        return s

    def __str__(self):
        self.refresh()
        indent = "  "
        s = self.device_characteristics_str(indent)
        s += indent + self.device_firmware_str(indent)
        s += indent + self.device_product_str(indent)
        s += indent + self.device_time_str(indent)
        s += indent + self.device_radio_str(indent)
        return s

    ############################################################################
    #                                                                          #
    #                            Workflow Methods                              #
    #                                                                          #
    ############################################################################

    # Don't wait for Acks or Responses, just send the same message repeatedly as fast as possible
    def fire_and_forget(self, msg_type, payload={}, timeout_secs=DEFAULT_TIMEOUT, num_repeats=DEFAULT_ATTEMPTS):
        socket_id = self.initialize_socket(timeout_secs)
        sock = self.socket_table[socket_id]
        msg = msg_type(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=False,
                       response_requested=False)
        sent_msg_count = 0
        sleep_interval = 0.05 if num_repeats > 20 else 0
        while sent_msg_count < num_repeats:
            if self.ip_addr:
                sock.sendto(msg.packed_message, (self.ip_addr, self.port))
            else:
                for ip_addr in UDP_BROADCAST_IP_ADDRS:
                    sock.sendto(msg.packed_message, (ip_addr, self.port))
            if self.verbose:
                print("SEND: " + str(msg))
            sent_msg_count += 1
            sleep(sleep_interval)  # Max num of messages device can handle is 20 per second.
        self.close_socket(socket_id)

    # Usually used for Set messages
    def req_with_ack(self, msg_type, payload, timeout_secs=DEFAULT_TIMEOUT, max_attempts=DEFAULT_ATTEMPTS):
        self.req_with_resp(msg_type, Acknowledgement, payload, timeout_secs, max_attempts)

    # Usually used for Get messages, or for state confirmation after Set (hence the optional payload)
    def req_with_resp(self, msg_type, response_type, payload={}, timeout_secs=DEFAULT_TIMEOUT,
                      max_attempts=DEFAULT_ATTEMPTS):
        # Need to put error checking here for aguments
        if type(response_type) != type([]):
            response_type = [response_type]
        success = False
        device_response = None
        socket_id = self.initialize_socket(timeout_secs)
        sock = self.socket_table[socket_id]
        if len(response_type) == 1 and Acknowledgement in response_type:
            msg = msg_type(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=True,
                           response_requested=False)
        else:
            msg = msg_type(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=False,
                           response_requested=True)
        response_seen = False
        attempts = 0
        while not response_seen and attempts < max_attempts:
            sent = False
            start_time = time()
            timedout = False
            while not response_seen and not timedout:
                if not sent:
                    if self.ip_addr:
                        sock.sendto(msg.packed_message, (self.ip_addr, self.port))
                    else:
                        for ip_addr in UDP_BROADCAST_IP_ADDRS:
                            sock.sendto(msg.packed_message, (ip_addr, self.port))
                    sent = True
                    if self.verbose:
                        print("SEND: " + str(msg))
                try:
                    data, (ip_addr, port) = sock.recvfrom(1024)
                    response = unpack_lifx_message(data)
                    if self.verbose:
                        print("RECV: " + str(response))
                    if type(response) in response_type:
                        if response.source_id == self.source_id and (
                                response.target_addr == self.mac_addr or response.target_addr == BROADCAST_MAC):
                            response_seen = True
                            device_response = response
                            self.ip_addr = ip_addr
                            success = True
                except timeout:
                    pass
                elapsed_time = time() - start_time
                timedout = True if elapsed_time > timeout_secs else False
            attempts += 1
        if not success:
            self.close_socket(socket_id)
            raise WorkflowException(
                "WorkflowException: Did not receive {} from {} (Name: {}) in response to {}".format(str(response_type),
                                                                                                    str(self.mac_addr),
                                                                                                    str(self.label),
                                                                                                    str(msg_type)))
        else:
            self.close_socket(socket_id)
        return device_response

    # Not currently implemented, although the LIFX LAN protocol supports this kind of workflow natively
    # def req_with_ack_resp(self, msg_type, response_type, payload, timeout_secs=DEFAULT_TIMEOUT,
    #                       max_attempts=DEFAULT_ATTEMPTS):
    #     pass

    ############################################################################
    #                                                                          #
    #                              Socket Methods                              #
    #                                                                          #
    ############################################################################

    def initialize_socket(self, timeout):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.settimeout(timeout)
        try:
            sock.bind(("", 0))  # allow OS to assign next available source port
            socket_id = self.socket_counter
            self.socket_table[socket_id] = sock
            self.socket_counter += 1
            return socket_id
        except Exception as err:
            raise WorkflowException("WorkflowException: error {} while trying to open socket".format(str(err)))

    def close_socket(self, socket_id):
        sock = self.socket_table.pop(socket_id, None)
        if sock is not None:
            sock.close()


################################################################################
#                                                                              #
#                             Formatting Functions                             #
#                                                                              #
################################################################################

def nanosec_to_hours(ns):
    return ns / (1000000000.0 * 60 * 60)
