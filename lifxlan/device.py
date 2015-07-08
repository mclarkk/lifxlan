# Import note: Every time you use a get_whatever() method, you are sending
# packets to the device. If you want to access the last known (cached) value of an attribute
# just access the attribute directly, e.g., mydevice.label instead of mydevice.get_label()

# Currently service and port are set during initialization and bever changed.
# This may need to change in the future to support multiple (service, port) pairs
# per device, and also to capture in real time when a service is down (port = 0).

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, timeout
from msgtypes import *
from unpack import unpack_lifx_message
from time import time, sleep
from datetime import datetime

UDP_BROADCAST_IP = "255.255.255.255"
UDP_BROADCAST_PORT = 56700

class Device(object):
	def __init__(self, mac_addr, service, port, source_id):
		self.mac_addr = mac_addr
		self.port = port
		self.service = service
		self.source_id = source_id

		# The following attributes can be set by calling refresh(), but that 
		# takes time so it is not done by default during initialization.
		# However, refresh() will be called each time __str__ is called.
		# Printing the device is therefore accurate but expensive.
		self.label = None
		self.power_level = None
		self.host_firmware_build_timestamp = None
		self.host_firmware_version = None
		self.wifi_firmware_build_timestamp = None
		self.wifi_firmware_version = None
		self.vendor = None
		self.product = None
		self.version = None

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

	# update the relatively persistent attributes
	def refresh(self):
		self.label = self.get_label()
		self.power_level = self.get_power()
		# for efficiency, initialize host, wifi, and version attributes all at once
		self.host_firmware_build_timestamp, self.host_firmware_version = self._get_host_firmware()
		self.wifi_firmware_build_timestamp, self.wifi_firmware_version = self._get_wifi_firmware()
		self.vendor, self.product, self.version = self._get_version()

	def get_mac_addr(self):
		return self.mac_addr

	# GetService - service, port
	def get_service(self):
		return self.service

	def get_port(self):
		return self.port

	#GetLabel - label
	def get_label(self):
		try:
			response = self.req_with_resp(GetLabel, StateLabel)
			self.label = response.label
		except:
			pass
		return self.label

	def set_label(self, label):
		if len(label) > 32:
			label = label[:32]
		self.req_with_ack(SetLabel, {"label": label})

	# GetPower - power level
	def get_power(self):
		try:
			response = self.req_with_resp(GetPower, StatePower)
			self.power_level = response.power_level
		except:
			pass
		return self.power_level

	def set_power(self, power):
		on = [True, 1, "on"]
		off = [False, 0, "off"]
		if power in on:
			success = self.req_with_ack(SetPower, {"power_level": 65535})
		elif power in off:
			success = self.req_with_ack(SetPower, {"power_level": 0})

	#GetHostFirmware - build, version
	def _get_host_firmware(self):
		build = None
		version = None
		try:
			response = self.req_with_resp(GetHostFirmware, StateHostFirmware)
			build = response.build
			version = response.version
		except:
			pass
		return build, version

	def get_host_firmware_build_timestamp(self):
		self.host_firmware_build_timestamp, self.host_firmware_version = self._get_host_firmware()
		return self.host_firmware_build_timestamp

	def get_host_firmware_version(self):
		self.host_firmware_build_timestamp, self.host_firmware_version = self._get_host_firmware()
		return self.host_firmware_version

	#GetWifiInfo - signal, tx, rx
	def _get_wifi_info(self):
		signal = None
		tx = None
		rx = None
		try:
			response = self.req_with_resp(GetWifiInfo, StateWifiInfo)
			signal = response.signal
			tx = response.tx
			rx = response.rx
		except:
			pass
		return signal, tx, rx

	def get_wifi_signal_mw(self):
		signal, tx, rx = self._get_wifi_info()
		return signal

	def get_wifi_tx_bytes(self):
		signal, tx, rx = self._get_wifi_info()
		return tx

	def get_wifi_rx_bytes(self):
		signal, tx, rx = self._get_wifi_info()
		return rx

	#GetWifiFirmware - build, version
	def _get_wifi_firmware(self):
		build = None
		version = None
		try:
			response = self.req_with_resp(GetWifiFirmware, StateWifiFirmware)
			build = response.build
			version = response.version
		except:
			pass
		return build, version

	def get_wifi_firmware_build_timestamp(self):
		self.wifi_firmware_build_timestamp, self.wifi_firmware_version = self._get_wifi_firmware()
		return self.wifi_firmware_build_timestamp

	def get_wifi_firmware_version(self):
		self.wifi_firmware_build_timestamp, self.wifi_firmware_version = self._get_wifi_firmware()
		return self.wifi_firmware_version

	#GetVersion - vendor product version 
	def _get_version(self):
		vendor = None
		product = None
		version = None
		try:
			response = self.req_with_resp(GetVersion, StateVersion)
			vendor = response.vendor
			product = response.product
			version = response.version
		except:
			pass
		return vendor, product, version

	def get_vendor(self):
		self.vendor, self.product, self.version = self._get_version()
		return self.vendor

	def get_product(self):
		self.vendor, self.product, self.version = self._get_version()
		return self.product

	def get_version(self):
		self.vendor, self.product, self.version = self._get_version()
		return self.version

	#GetInfo - time uptime downtime
	def _get_info(self):
		time = None
		uptime = None
		downtime = None
		try:
			response = self.req_with_resp(GetInfo, StateInfo)
			time = response.time
			uptime = response.uptime
			downtime = response.downtime
		except:
			pass
		return time, uptime, downtime

	def get_time(self):
		time, uptime, downtime = self._get_info()
		return time

	def get_uptime(self):
		time, uptime, downtime = self._get_info()
		return uptime

	def get_downtime(self):
		time, uptime, downtime = self._get_info()
		return downtime

	def device_characteristics_str(self, indent):
		s = "{}\n".format(self.label)
		s += indent + "MAC Address: {}\n".format(self.mac_addr)
		s += indent + "Port: {}\n".format(self.port)
		s += indent + "Service: {}\n".format(SERVICE_IDS[self.service])
		s += indent + "Power: {}\n".format(STR_MAP[self.power_level])
		return s

	def device_firmware_str(self, indent):
		host_build_ns = self.host_firmware_build_timestamp
		host_build_s = host_build_ns/1000000000
		wifi_build_ns = self.wifi_firmware_build_timestamp
		wifi_build_s = wifi_build_ns/1000000000
		s = "Host Firmware Build Timestamp: {} ({} UTC)\n".format(host_build_ns, datetime.utcfromtimestamp(host_build_s))
		s += indent + "Host Firmware Build Version: {}\n".format(self.host_firmware_version)
		s += indent + "Wifi Firmware Build Timestamp: {} ({} UTC)\n".format(wifi_build_ns, datetime.utcfromtimestamp(wifi_build_s))
		s += indent + "Wifi Firmware Build Version: {}\n".format(self.wifi_firmware_version)
		return s

	def device_product_str(self, indent):
		s = "Vendor: {}\n".format(self.vendor)
		s += indent + "Product: {}\n".format(self.product)
		s += indent + "Version: {}\n".format(self.version)
		return s

	def device_time_str(self, indent):
		time, uptime, downtime = self._get_info()
		s = "Current Time: {} ({} UTC)\n".format(time, datetime.utcfromtimestamp(time/1000000000))
		s += indent + "Uptime (ns): {} ({} hours)\n".format(uptime, round(nanosec_to_hours(uptime), 2))
		s += indent + "Last Downtime Duration +/-5s (ns): {} ({} hours)\n".format(downtime, round(nanosec_to_hours(downtime), 2))
		return s

	def device_radio_str(self, indent):
		signal, tx, rx = self._get_wifi_info()
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


	#### Send functions

	def fire_and_forget(self, msgtype, payload={}, timeout_secs=0.5, num_repeats=5):
		self.initialize_socket(timeout_secs)
		msg = msgtype(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=False, response_requested=True)
		sent_msg_count = 0
		sleep_interval = 0.05 if num_repeats > 20 else 0
		while(sent_msg_count < num_repeats):
			self.sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, self.port))
			sent_msg_count += 1
			sleep(sleep_interval) # Max num of messages device can handle is 20 per second.
		self.close_socket()

	# Usually used for Set messages
	def req_with_ack(self, msgtype, payload, timeout_secs=0.5, max_attempts=5):
		success = False
		self.initialize_socket(timeout_secs)
		msg = msgtype(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=True, response_requested=False)	
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
				try:
					data = self.sock.recv(1024)
					response = unpack_lifx_message(data)
					if type(response) == Acknowledgement:
						if response.origin == 1 and response.source_id == self.source_id and response.target_addr == self.mac_addr:
							response_seen = True
							success = True
				except timeout:
					pass
				elapsed_time = time() - start_time
				timedout = True if elapsed_time > timeout_secs else False
			attempts += 1
		if not success:
			raise NoAckException("Problem sending " + str(msgtype))
		self.close_socket()

	# Usually used for Get messages, optionally for state confirmation after Set (hence the optional payload)
	def req_with_resp(self, msgtype, response_type, payload={}, timeout_secs=0.5, max_attempts=5):
		device_response = None
		self.initialize_socket(timeout_secs)
		msg = msgtype(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=False, response_requested=True)	
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
				try: 
					data = self.sock.recv(1024)
					response = unpack_lifx_message(data)
					if type(response) == response_type:
						if response.origin == 1 and response.source_id == self.source_id and response.target_addr == self.mac_addr:
							response_seen = True
							device_response = response
				except timeout:
					pass
				elapsed_time = time() - start_time
				timedout = True if elapsed_time > timeout_secs else False
			attempts += 1
		if device_response == None:
			raise NoResponseException("Problem sending " + str(msgtype))
		self.close_socket()
		return device_response

	def req_with_ack_resp(self, msgtype, response_type, payload, timeout_secs=0.5, max_attempts=5):
		pass

	def initialize_socket(self, timeout):
		self.sock = socket(AF_INET, SOCK_DGRAM)
		self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		self.sock.settimeout(timeout)
		port = UDP_BROADCAST_PORT
		self.sock.bind(("", port))

	def close_socket(self):
		self.sock.close()

class WorkflowException(Exception):
	pass

class NoResponseException(WorkflowException):
    pass

class NoAckException(WorkflowException):
	pass

def nanosec_to_hours(ns):
	return ns/(1000000000.0*60*60)