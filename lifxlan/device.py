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

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, timeout, error
from .msgtypes import *
from .unpack import unpack_lifx_message
from time import time, sleep
from datetime import datetime
from .products import product_map
from .products import features_map
from .errors import WorkflowException, InvalidParameterException

DEFAULT_TIMEOUT = 0.5
DEFAULT_ATTEMPTS = 5

UDP_BROADCAST_IP = "255.255.255.255"
UDP_BROADCAST_PORT = 56700

VERBOSE = False

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
        self.ip_addr = ip_addr # IP addresses can change, though...

        # The following attributes can be set by calling refresh(), but that
        # takes time so it is not done by default during initialization.
        # However, refresh() will be called each time __str__ is called.
        # Printing the device is therefore accurate but expensive.

        self.label = None
        self.location = None
        self.group = None
        self.power_level = None
        self.host_firmware_build_timestamp = None
        self.host_firmware_version = None
        self.wifi_firmware_build_timestamp = None
        self.wifi_firmware_version = None
        self.vendor = None
        self.product = None
        self.version = None
        self.product_name = None
        self.product_features = None

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


    ############################################################################
    #                                                                          #
    #                            Device API Methods                            #
    #                                                                          #
    ############################################################################

    # update the device's (relatively) persistent attributes
    def refresh(self):
        self.label = self.get_label()
        self.location = self.get_location()
        self.group = self.get_group()
        self.power_level = self.get_power()
        self.host_firmware_build_timestamp, self.host_firmware_version = self.get_host_firmware_tuple()
        self.wifi_firmware_build_timestamp, self.wifi_firmware_version = self.get_wifi_firmware_tuple()
        self.vendor, self.product, self.version = self.get_version_tuple()
        self.product_name = self.get_product_name()
        self.product_features = self.get_product_features()

    def get_mac_addr(self):
        return self.mac_addr

    def get_service(self):
        return self.service

    def get_port(self):
        return self.port

    def get_ip_addr(self):
        return self.ip_addr

    def get_source_id(self):
        return self.source_id

    def get_label(self):
        try:
            response = self.req_with_resp(GetLabel, StateLabel)
            self.label = response.label.replace("\x00", "")
        except:
            raise
        return self.label

    def get_label(self):
         try:
             response = self.req_with_resp(GetLabel, StateLabel)
         except:
             return self.label
         try:
             self.label = response.label.replace("\x00", "")
         except:
            try:
                self.label = response.label.decode().replace("\x00", "")
            except:
                raise
         return self.label

    def get_location(self):
        try:
            response = self.req_with_resp(GetLocation, StateLocation)
            self.location = response.label.replace("\x00", "")
        except:
            raise
        return self.location

    def get_group(self):
        try:
            response = self.req_with_resp(GetGroup, StateGroup)
            self.group = response.label.replace("\x00", "")
        except:
            raise
        return self.group

    def set_label(self, label):
        if len(label) > 32:
            label = label[:32]
        self.req_with_ack(SetLabel, {"label": label})

    def get_power(self):
        try:
            response = self.req_with_resp(GetPower, StatePower)
            self.power_level = response.power_level
        except:
            raise
        return self.power_level

    def set_power(self, power, rapid=False):
        on = [True, 1, "on"]
        off = [False, 0, "off"]
        if power in on and not rapid:
            success = self.req_with_ack(SetPower, {"power_level": 65535})
        elif power in off and not rapid:
            success = self.req_with_ack(SetPower, {"power_level": 0})
        elif power in on and rapid:
            success = self.fire_and_forget(SetPower, {"power_level": 65535})
        elif power in off and rapid:
            success = self.fire_and_forget(SetPower, {"power_level": 0})

    def get_host_firmware_tuple(self):
        build = None
        version = None
        try:
            response = self.req_with_resp(GetHostFirmware, StateHostFirmware)
            build = response.build
            version = float(str(str(response.version >> 16) + "." + str(response.version & 0xff)))
        except:
            raise
        return build, version

    def get_host_firmware_build_timestamp(self):
        self.host_firmware_build_timestamp, self.host_firmware_version = self.get_host_firmware_tuple()
        return self.host_firmware_build_timestamp

    def get_host_firmware_version(self):
        self.host_firmware_build_timestamp, self.host_firmware_version = self.get_host_firmware_tuple()
        return self.host_firmware_version

    def get_wifi_info_tuple(self):
        signal = None
        tx = None
        rx = None
        try:
            response = self.req_with_resp(GetWifiInfo, StateWifiInfo)
            signal = response.signal
            tx = response.tx
            rx = response.rx
        except:
            raise
        return signal, tx, rx

    def get_wifi_signal_mw(self):
        signal, tx, rx = self.get_wifi_info_tuple()
        return signal

    def get_wifi_tx_bytes(self):
        signal, tx, rx = self.get_wifi_info_tuple()
        return tx

    def get_wifi_rx_bytes(self):
        signal, tx, rx = self.get_wifi_info_tuple()
        return rx

    def get_wifi_firmware_tuple(self):
        build = None
        version = None
        try:
            response = self.req_with_resp(GetWifiFirmware, StateWifiFirmware)
            build = response.build
            version = float(str(str(response.version >> 16) + "." + str(response.version & 0xff)))
        except:
            raise
        return build, version

    def get_wifi_firmware_build_timestamp(self):
        self.wifi_firmware_build_timestamp, self.wifi_firmware_version = self.get_wifi_firmware_tuple()
        return self.wifi_firmware_build_timestamp

    def get_wifi_firmware_version(self):
        self.wifi_firmware_build_timestamp, self.wifi_firmware_version = self.get_wifi_firmware_tuple()
        return self.wifi_firmware_version

    def get_version_tuple(self):
        vendor = None
        product = None
        version = None
        try:
            response = self.req_with_resp(GetVersion, StateVersion)
            vendor = response.vendor
            product = response.product
            version = response.version
        except:
            raise
        return vendor, product, version

    def get_product_name(self):
        product_name = None
        if self.product == None:
            self.vendor, self.product, self.version = self.get_version_tuple()
        if self.product in product_map:
            product_name = product_map[self.product]
        return product_name

    def get_product_features(self):
        product_features = None
        if self.product == None:
            self.vendor, self.product, self.version = self.get_version_tuple()
        if self.product in product_map:
            product_features = features_map[self.product]
        return product_features

    def get_vendor(self):
        self.vendor, self.product, self.version = self.get_version_tuple()
        return self.vendor

    def get_product(self):
        self.vendor, self.product, self.version = self.get_version_tuple()
        return self.product

    def get_version(self):
        self.vendor, self.product, self.version = self.get_version_tuple()
        return self.version

    def get_location_tuple(self):
        label = None
        updated_at = None
        try:
            response = self.req_with_resp(GetLocation, StateLocation)
            self.location = response.location
            label = response.label.replace("\x00", "")
            updated_at = response.updated_at
        except:
            raise
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
            label = response.label.replace("\x00", "")
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

    def get_info_tuple(self):
        time = None
        uptime = None
        downtime = None
        try:
            response = self.req_with_resp(GetInfo, StateInfo)
            time = response.time
            uptime = response.uptime
            downtime = response.downtime
        except:
            raise
        return time, uptime, downtime

    def get_time(self):
        time, uptime, downtime = self.get_info_tuple()
        return time

    def get_uptime(self):
        time, uptime, downtime = self.get_info_tuple()
        return uptime

    def get_downtime(self):
        time, uptime, downtime = self.get_info_tuple()
        return downtime

    def supports_color(self):
        if self.product_features == None:
            self.product_features = self.get_product_features()
        return self.product_features['color']

    def supports_multizone(self):
        if self.product_features == None:
            self.product_features = self.get_product_features()
        return self.product_features['multizone']

    def supports_infrared(self):
        if self.product_features == None:
            self.product_features = self.get_product_features()
        return self.product_features['infrared']

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
        host_build_s = datetime.utcfromtimestamp(host_build_ns/1000000000) if host_build_ns != None else None
        wifi_build_ns = self.wifi_firmware_build_timestamp
        wifi_build_s = datetime.utcfromtimestamp(wifi_build_ns/1000000000) if wifi_build_ns != None else None
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
        time, uptime, downtime = self.get_info_tuple()
        time_s = datetime.utcfromtimestamp(time/1000000000) if time != None else None
        uptime_s = round(nanosec_to_hours(uptime), 2) if uptime != None else None
        downtime_s = round(nanosec_to_hours(downtime), 2) if downtime != None else None
        s = "Current Time: {} ({} UTC)\n".format(time, time_s)
        s += indent + "Uptime (ns): {} ({} hours)\n".format(uptime, uptime_s)
        s += indent + "Last Downtime Duration +/-5s (ns): {} ({} hours)\n".format(downtime, downtime_s)
        return s

    def device_radio_str(self, indent):
        signal, tx, rx = self.get_wifi_info_tuple()
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
        self.initialize_socket(timeout_secs)
        msg = msg_type(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=False, response_requested=False)
        sent_msg_count = 0
        sleep_interval = 0.05 if num_repeats > 20 else 0
        while(sent_msg_count < num_repeats):
            self.sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, self.port))
            if self.verbose:
                print("SEND: " + str(msg))
            sent_msg_count += 1
            sleep(sleep_interval) # Max num of messages device can handle is 20 per second.
        self.close_socket()

    # Usually used for Set messages
    def req_with_ack(self, msg_type, payload, timeout_secs=DEFAULT_TIMEOUT, max_attempts=DEFAULT_ATTEMPTS):
        self.req_with_resp(msg_type, Acknowledgement, payload, timeout_secs, max_attempts)

    # Usually used for Get messages, or for state confirmation after Set (hence the optional payload)
    def req_with_resp(self, msg_type, response_type, payload={}, timeout_secs=DEFAULT_TIMEOUT, max_attempts=DEFAULT_ATTEMPTS):
        # Need to put error checking here for aguments
        if type(response_type) != type([]):
            response_type = [response_type]
        success = False
        device_response = None
        self.initialize_socket(timeout_secs)
        if len(response_type) == 1 and Acknowledgement in response_type:
            msg = msg_type(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=True, response_requested=False)
        else:
            msg = msg_type(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=False, response_requested=True)
        response_seen = False
        attempts = 0
        while not response_seen and attempts < max_attempts:
            sent = False
            start_time = time()
            timedout = False
            while not response_seen and not timedout:
                if not sent:
                    self.sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, self.port))
                    sent = True
                    if self.verbose:
                        print("SEND: " + str(msg))
                try:
                    data, (ip_addr, port) = self.sock.recvfrom(1024)
                    response = unpack_lifx_message(data)
                    if self.verbose:
                        print("RECV: " + str(response))
                    if type(response) in response_type:
                        if response.origin == 1 and response.source_id == self.source_id and response.target_addr == self.mac_addr:
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
            self.close_socket()
            raise WorkflowException("WorkflowException: Did not receive {} from {} (Name: {}) in response to {}".format(str(response_type), str(self.mac_addr), str(self.label), str(msg_type)))
        else:
            self.close_socket()
        return device_response

    # Not currently implemented, although the LIFX LAN protocol supports this kind of workflow natively
    def req_with_ack_resp(self, msg_type, response_type, payload, timeout_secs=DEFAULT_TIMEOUT, max_attempts=DEFAULT_ATTEMPTS):
        pass

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
        port = UDP_BROADCAST_PORT
        success = False
        while not success:
            try:
                self.sock.bind(("", port))
                success = True
            except: # address (port) already in use, maybe another client on the same computer...
                port += 1

    def close_socket(self):
        self.sock.close()

################################################################################
#                                                                              #
#                             Formatting Functions                             #
#                                                                              #
################################################################################

def nanosec_to_hours(ns):
    return ns/(1000000000.0*60*60)
