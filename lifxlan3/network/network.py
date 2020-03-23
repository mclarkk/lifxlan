import time
from socket import timeout
from typing import Optional, Dict, Type

import netifaces as ni

from .message import Message
from .unpack import unpack_lifx_message, Acknowledgement
from lifxlan3.settings import TOTAL_NUM_LIGHTS
from lifxlan3.utils import init_socket, init_log

__author__ = 'acushner'

log = init_log(__name__)


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
