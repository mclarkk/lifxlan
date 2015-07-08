from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, timeout
from message import BROADCAST_MAC, BROADCAST_SOURCE_ID
from device import Device, UDP_BROADCAST_IP, UDP_BROADCAST_PORT
from light import *
from msgtypes import *
from unpack import unpack_lifx_message
from random import randint
from time import time, sleep

class LifxLAN:
	def __init__(self, num_lights=None, verbose=False):
		self.source_id = randint(0, (2**32)-1)
		self.num_devices = num_lights
		self.devices = []
		self.verbose = verbose

	############################################################################
	#                                                                          #
	#                         LAN (Broadcast) API Methods                      #
	#                                                                          #
	############################################################################

	def get_devices(self):
		if self.num_devices == None:
			responses = self.discover()
		else:
			responses = self.broadcast_with_resp(GetService, StateService)
		for r in responses:
			mac = r.target_addr
			service = r.service
			port = r.port
			self.devices.append(Device(mac, service, port, self.source_id, self.verbose))
		self.num_devices = len(self.devices)
		return self.devices

	def get_lights(self):
		if self.num_devices == None:
			responses = self.discover()
		else:
			responses = self.broadcast_with_resp(GetService, StateService)
		for r in responses:
			mac = r.target_addr
			service = r.service
			port = r.port
			self.devices.append(Light(mac, service, port, self.source_id, self.verbose))
		self.num_devices = len(self.devices)
		return self.devices

	# set_all_power(on/off)

	# set_all_color(color, duration, rapid)

	############################################################################
	#                                                                          #
	#                            Workflow Methods                              #     
	#                                                                          #
	############################################################################

	def discover(self, timeout_secs=1, num_repeats=3):
		self.initialize_socket(timeout_secs)
		msg = GetService(BROADCAST_MAC, self.source_id, seq_num=0, payload={}, ack_requested=False, response_requested=True)	
		responses = []
		addr_seen = []
		num_devices_seen = 0
		attempts = 0
		while attempts < num_repeats:
			sent = False
			start_time = time()
			timedout = False
			while not timedout:
				if not sent:
					self.sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, UDP_BROADCAST_PORT))
					sent = True
					if self.verbose:
						print("SEND: " + str(msg))
				try: 
					data = self.sock.recv(1024)
					response = unpack_lifx_message(data)
					if self.verbose:
						print("RECV: " + str(response))
					if type(response) == StateService and response.origin == 1 and response.source_id == self.source_id:
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

	def broadcast_fire_and_forget(self, msg_type, payload={}, timeout_secs=0.5, num_repeats=5):
		self.initialize_socket(timeout_secs)
		msg = msg_type(BROADCAST_MAC, self.source_id, seq_num=0, payload=payload, ack_requested=False, response_requested=False)
		sent_msg_count = 0
		sleep_interval = 0.05 if num_repeats > 20 else 0
		while(sent_msg_count < num_repeats):
			self.sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, UDP_BROADCAST_PORT))
			if self.verbose:
						print("SEND: " + str(msg))
			sent_msg_count += 1
			sleep(sleep_interval) # Max num of messages device can handle is 20 per second.
		self.close_socket()

	def broadcast_with_resp(self, msg_type, response_type, payload={}, timeout_secs=3, max_attempts=5):
		success = False
		self.initialize_socket(timeout_secs)
		if response_type == Acknowledgement:
			msg = msg_type(BROADCAST_MAC, self.source_id, seq_num=0, payload=payload, ack_requested=True, response_requested=False)	
		else:
			msg = msg_type(BROADCAST_MAC, self.source_id, seq_num=0, payload=payload, ack_requested=False, response_requested=True)
		responses = []
		addr_seen = []
		num_devices_seen = 0
		attempts = 0
		while num_devices_seen < self.num_devices and attempts < max_attempts:
			sent = False
			start_time = time()
			timedout = False
			while num_devices_seen < self.num_devices and not timedout:
				if not sent:
					self.sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, UDP_BROADCAST_PORT))
					sent = True
					if self.verbose:
						print("SEND: " + str(msg))
				try: 
					data = self.sock.recv(1024)
					response = unpack_lifx_message(data)
					if self.verbose:
						print("RECV: " + str(response))
					if type(response) == response_type and response.origin == 1 and response.source_id == self.source_id:
						if response.target_addr not in addr_seen and response.target_addr != BROADCAST_MAC:
							addr_seen.append(response.target_addr)
							num_devices_seen += 1
							responses.append(response)
							if num_devices_seen >= self.num_devices:
								success = True
				except timeout:
					pass
				elapsed_time = time() - start_time
				timedout = True if elapsed_time > timeout_secs else False
			attempts += 1
		if success == False:
			raise WorkflowException("Did not receive {} in response to {}".format(str(response_type), str(msg_type)))
		self.close_socket()
		return responses

	def broadcast_with_ack(self, msg_type, response_type, payload={}, timeout_sec=3, max_attempts=5):
		broadcast_with_resp(msg_type, Acknowlegement, payload, timeout_secs, max_attempts)

	# Not currently implemented, although the LIFX LAN protocol supports this kind of workflow natively
	def broadcast_with_ack_resp(self, msg_type, response_type, payload={}, timeout_sec=3):
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
		self.sock.bind(("", port))

	def close_socket(self):
		self.sock.close()

def test():
	pass

if __name__=="__main__":
	test()