# lifxlan

**lifxlan** is a Python module for locally controlling LIFX devices (such as lightbulbs) over a LAN. 

## How to Install

`sudo python setup.py install`

## Run

See the `examples` folder for example scripts that use **lifxlan**.  

## Overview

There are several things you can do with this library:

* Control LIFX devices using the high-level API (see the `examples` folder).
* Build your own high-level API on top of the low-level networking messages.
* Build virtual LIFX devices in software (think adapters for Philips Hue bulbs, Wemo, etc).

I find the last option particularly exciting. You can use the low-level networking library to create messages that LIFX devices send to clients, effectively simulating a LIFX device in software. What that means is that you can write a software program that looks and acts like a LIFX device, but is really, say, converting SetColor and/or SetPower messages into API calls for other systems, like Philips Hue bulbs and Wemos.

Long story short, you can use this library to build a program that makes your other RGB lightbulbs and on/off devices show up in your LIFX app. Control your Philips Hue bulbs and Wemos through the LIFX app! Whoa!

#### High-Level API:

* device.py (descr)
* light.py (descr)
* lifxlan.py (descr)

#### LIFX LAN Protocol:

The LIFX LAN protocol is officially documented [here](https://github.com/LIFX/lifx-protocol-docs).
* message.py (descr)
* msgtypes.py (descr)
* unpack.py (descr)