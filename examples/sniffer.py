#!/usr/bin/env python
# coding=utf-8
# sniffer.py
# Author: Meghan Clark
# Listens to broadcast UDP messages. If you are using the LIFX app to control a bulb,
# you might see some things.


from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, socket, timeout

from lifxlan import UDP_BROADCAST_IP_ADDRS, UDP_BROADCAST_PORT, unpack_lifx_message


class Sniffer(object):
    def __init__(self):
        self.port = UDP_BROADCAST_PORT
        self.sock = None
        self.sniff()

    def sniff(self):
            self.initialize_socket()
            try:
                while(True):
                    try:
                        data = self.sock.recv(1024)
                        request = unpack_lifx_message(data)
                        print("\nRECV:"),
                        print(request)
                    except timeout:
                        pass
            except KeyboardInterrupt:
                self.sock.close()

    def send(self, msg):
        if self.sock == None:
            self.initialize_socket()
        msg.origin = 1
        print("SEND:"),
        print(msg)
        for broadcast_addr in UDP_BROADCAST_IP_ADDRS:
            self.sock.sendto(msg.packed_message, (broadcast_addr, self.port))

    def initialize_socket(self):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock.settimeout(0.5)
        port = UDP_BROADCAST_PORT
        self.sock.bind(("", port))

if __name__ == "__main__":
    Sniffer()
