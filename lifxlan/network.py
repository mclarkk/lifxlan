import logging
from contextlib import suppress
from socket import timeout
from typing import Optional, Dict, Type, List, Union

# from lifxlan import NoResponse
from .unpack import unpack_lifx_message, Acknowledgement
from .message import Message

from .utils import init_socket
import netifaces as ni
import time
from .settings import TOTAL_NUM_LIGHTS

__author__ = 'acushner'

log = logging.getLogger(__name__)


def _get_broadcast_addrs():
    broadcast_addrs = []
    for iface in ni.interfaces():
        try:
            ifaddr = ni.ifaddresses(iface)[ni.AF_INET][0]
            if ifaddr['addr'] != '127.0.0.1':
                broadcast_addrs.append(ifaddr['broadcast'])
        except:  # for interfaces that don't support ni.AF_INET
            pass
    return broadcast_addrs


UDP_BROADCAST_IP_ADDRS = _get_broadcast_addrs()
UDP_BROADCAST_PORT = 56700
DEFAULT_TIMEOUT = .7  # second
DEFAULT_ATTEMPTS = 4
BROADCAST_MAC = "00:00:00:00:00:00"
MessageType = Type[Message]


def broadcast_with_resp(msg_type: MessageType, response_type: MessageType, source_id, payload: Optional[Dict] = None,
                        timeout_secs=DEFAULT_TIMEOUT,
                        max_attempts=DEFAULT_ATTEMPTS,
                        total_num_lights=TOTAL_NUM_LIGHTS,
                        *, verbose=False):
    payload = payload or {}
    msg = _create_msg(msg_type, response_type, source_id, payload)
    responses = []
    addr_seen = set()
    attempts = 0

    def found_all_lights():
        return not (total_num_lights is None or len(addr_seen) < total_num_lights)

    with init_socket(timeout_secs) as sock:
        while not found_all_lights() and attempts < max_attempts:
            sent = False
            start_time = time.time()
            timedout = False
            attempts += 1

            while not found_all_lights() and not timedout:
                if not sent:
                    for ip_addr in UDP_BROADCAST_IP_ADDRS:
                        sock.sendto(msg.packed_message, (ip_addr, UDP_BROADCAST_PORT))
                    sent = True
                    if verbose:
                        print("SEND: " + str(msg))

                try:
                    response = _get_response(response_type, source_id, sock, verbose)
                    if response.target_addr not in addr_seen and response.target_addr != BROADCAST_MAC:
                        addr_seen.add(response.target_addr)
                        responses.append(response)
                except timeout:
                    timedout = time.time() - start_time > timeout_secs
    return responses


def _create_msg(msg_type, response_type, source_id, payload):
    if response_type == Acknowledgement:
        return msg_type(BROADCAST_MAC, source_id, seq_num=0, payload=payload, ack_requested=True,
                        response_requested=False)

    return msg_type(BROADCAST_MAC, source_id, seq_num=0, payload=payload, ack_requested=False,
                    response_requested=True)


def _get_response(response_type, source_id, sock, verbose):
    data, (ip_addr, port) = sock.recvfrom(1024)
    response = unpack_lifx_message(data)
    response.ip_addr = ip_addr
    if verbose:
        print("RECV: " + str(response))
    if type(response) == response_type and response.source_id == source_id:
        return response

# Not currently implemented, although the LIFX LAN protocol supports this kind of workflow natively
# def _broadcast_with_ack_resp(msg_type, response_type, payload={}, timeout_secs=DEFAULT_TIMEOUT + 0.5,
#                             max_attempts=DEFAULT_ATTEMPTS):
#     raise NotImplementedError

# ======================================================================================================================
# TODO: from device
# ======================================================================================================================
# def _send_set_message(self, msg_type, payload: Optional[Dict] = None, timeout_secs=DEFAULT_TIMEOUT,
#                       max_attempts=DEFAULT_ATTEMPTS, *, rapid: bool):
#     """handle sending messages either rapidly or not"""
#     args = msg_type, payload, timeout_secs
#     if rapid:
#         self.fire_and_forget(*args, num_repeats=max_attempts)
#     else:
#         self.req_with_ack(*args)
#
#
# # Don't wait for Acks or Responses, just send the same message repeatedly as fast as possible
# def fire_and_forget(self, msg_type, payload: Optional[Dict] = None, timeout_secs=DEFAULT_TIMEOUT,
#                     num_repeats=DEFAULT_ATTEMPTS):
#     payload = payload or {}
#     with init_socket(timeout_secs) as sock:
#         msg = msg_type(self.mac_addr, self.source_id, seq_num=0, payload=payload, ack_requested=False,
#                        response_requested=False)
#         sent_msg_count = 0
#         sleep_interval = 0.05 if num_repeats > 20 else 0
#         while sent_msg_count < num_repeats:
#             if self.ip_addr:
#                 sock.sendto(msg.packed_message, (self.ip_addr, self.port))
#             else:
#                 for ip_addr in UDP_BROADCAST_IP_ADDRS:
#                     sock.sendto(msg.packed_message, (ip_addr, self.port))
#             if self.verbose:
#                 print("SEND: " + str(msg))
#             sent_msg_count += 1
#             time.sleep(sleep_interval)  # Max num of messages device can handle is 20 per second.
#
#
# # Usually used for Set messages
# def req_with_ack(self, msg_type, payload, timeout_secs=DEFAULT_TIMEOUT, max_attempts=DEFAULT_ATTEMPTS):
#     self.req_with_resp(msg_type, Acknowledgement, payload, timeout_secs, max_attempts)
#
#
# # Usually used for Get messages, or for state confirmation after Set (hence the optional payload)
# def req_with_resp(self, msg_type: MessageType, response_type: Union[MessageType, List[MessageType]],
#                   source_id, device_ip_addr, device_port, mac_addr, label,
#                   payload: Optional[Dict] = None, timeout_secs=DEFAULT_TIMEOUT, max_attempts=DEFAULT_ATTEMPTS,
#                   *, verbose=False):
#     # Need to put error checking here for arguments
#     payload = payload or {}
#     if not isinstance(response_type, list):
#         response_type = [response_type]
#
#     success = False
#     device_response = None
#
#     with init_socket(timeout_secs) as sock:
#         ack_requested = len(response_type) == 1 and Acknowledgement in response_type
#         msg = msg_type(mac_addr, source_id, seq_num=0, payload=payload, ack_requested=ack_requested,
#                        response_requested=not ack_requested)
#         response_seen = False
#         attempts = 0
#         while not response_seen and attempts < max_attempts:
#             sent = False
#             start_time = time.time()
#             timedout = False
#             attempts += 1
#
#             ip_addrs = [device_ip_addr] if device_ip_addr else UDP_BROADCAST_IP_ADDRS
#             while not response_seen and not timedout:
#                 if not sent:
#                     for ip in ip_addrs:
#                         sock.sendto(msg.packed_message, (ip, device_port))
#                     sent = True
#                     if verbose:
#                         print("SEND: " + str(msg))
#                 try:
#                     data, (ip_addr, port) = sock.recvfrom(1024)
#                     response = unpack_lifx_message(data)
#                     if verbose:
#                         print("RECV: " + str(response))
#                     if type(response) in response_type:
#                         if response.source_id == source_id and (
#                                 response.target_addr == mac_addr or response.target_addr == BROADCAST_MAC):
#                             response_seen = True
#                             device_response = response
#                             device_ip_addr = ip_addr
#                             success = True
#                 except timeout:
#                     timedout = (time.time() - start_time) > timeout_secs
#         if not success:
#             raise NoResponse(f'WorkflowException: Did not receive {response_type!r} from {mac_addr!r} '
#                              f'(Name: {label!r}) in response to {msg_type!r}')
#         return device_response
