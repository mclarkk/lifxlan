# lifxlan

**lifxlan** is a Python module for locally controlling LIFX devices (such as lightbulbs) over a LAN. 

## How to Install

* TO DO

## Overview

This library has two parts: 1) an implementation of the low-level LIFX network protocol, and 2) a high-level library for locally controlling LIFX devices which is built on top of the low-level library. If the high-level abstractions don't work for you, you can easily build your own abstractions using the low-level network messages. 

#### LIFX LAN Protocol:

The LIFX LAN protocol is officially documented [here](https://github.com/LIFX/lifx-protocol-docs).
* message.py (descr)
* msgtypes.py (descr)
* unpack.py (descr)

#### High-Level API:

* device.py (descr)
* light.py (descr)
* lifxlan.py (descr)

## Examples

* TO DO
