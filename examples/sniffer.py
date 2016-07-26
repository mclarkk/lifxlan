#!/usr/bin/env python
# sniffer.py
# Author: Meghan Clark
# Listens to broadcast UDP messages. If you are using the LIFX app to control a bulb,
# you might see some things.

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST, timeout
from lifxlan import *
from time import time

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
        self.sock.sendto(msg.packed_message, (UDP_BROADCAST_IP, self.port))

    def initialize_socket(self):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock.settimeout(0.5)
        port = UDP_BROADCAST_PORT
        self.sock.bind(("", port))

if __name__ == "__main__":
    Sniffer()
