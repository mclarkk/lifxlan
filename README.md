# lifxlan

**lifxlan** is a Python module for locally controlling LIFX devices (such as lightbulbs) over a LAN. 

## How to Install

`sudo pip install lifxlan`

Or you can install from source with:

`sudo python setup.py install`

## Run

See the `examples` folder for example scripts that use **lifxlan**.  

## Overview

You can do several things with this library:

* Control LIFX devices using the high-level API (see the `examples` folder).
* Build your own high-level API on top of the low-level networking messages.
* Build virtual LIFX devices in software (think adapters for Philips Hue bulbs, Wemo, etc).

That's right, you can also use the low-level networking library to create messages that LIFX *devices* send to *clients*, effectively simulating a LIFX device in software. That means you can write a software program that looks and acts like a LIFX device, but is really converting SetColor and/or SetPower messages into API calls for other RGB lightbulbs or on/off devices, like Philips Hue bulbs and Wemos.

TL;DR: Theoretically, you can use this library to write proxy programs that let you view and control your Hue lights and Wemos through the LIFX app! Whoa!

#### High-Level API:

* **lifxlan.py** - Provides the LifxLAN API, and low-level API for sending broadcast LIFX packets to the LAN.
* **device.py** - Provides the Device API, and low-level API for sending unicast LIFX packets to a Device.
* **light.py** - Provides the Light API. Subclass of Device.

##### LifxLAN API

```
get_devices()
get_lights()
set_all_power(power, [duration], [rapid])
set_all_color(color, [duration], [rapid])
```

##### Device API

```
get_mac_addr()
get_service()
get_port()
get_label()
get_power()
get_host_firmware_tuple()
get_host_firmware_build_timestamp()
get_host_firmware_version()
get_wifi_info_tuple()
get_wifi_signal_mw()
get_wifi_tx_bytes()
get_wifi_rx_bytes()
get_wifi_firmware_tuple()
get_wifi_firmware_build_timestamp()
get_wifi_firmware_version()
get_version_tuple()
get_vendor()
get_product()
get_version()
get_info_tuple()
get_time()
get_uptime()
get_downtime()

set_label(label)
set_power(power)
```

##### Light API

The Light API provides all of the call in the Device API, as well as:

```
get_power()
get_color()

set_power(power, [duration], [rapid]):
set_color(color, [duration], [rapid]):
```


#### LIFX LAN Protocol:

The LIFX LAN protocol is officially documented [here](https://github.com/LIFX/lifx-protocol-docs). In lifxlan, you can see the underlying stream of packets being sent and received at any time by initializing the LifxLAN object with the verbose flag set: `lifx = LifxLAN(verbose = True)` (see `examples/verbose_lan.py`.)

The files that deal with LIFX packet construction and representation are:

* **message.py** -  Defines the message fields and the basic packet structure.
* **msgtypes.py** - Provides subclasses for each LIFX message type, along with their payload constructors.
* **unpack.py** - Creates a LIFX message object from a string of binary data (crucial for receiving messages).

Happy hacking!