# lifxlan

**lifxlan** is a Python 2 module for locally controlling LIFX devices (such as lightbulbs) over a LAN. It implements the [LIFX LAN Protocol V2](https://github.com/LIFX/lifx-protocol-docs) specification.

## How to Install

To get the latest stable release:

`sudo pip install lifxlan`

However, to be guaranteed to get the most recent features and fixes you can install from source with:

`sudo python setup.py install`

## Run

See the `examples` folder for example scripts that use **lifxlan**.  

Many of the examples perform device discovery in the beginning in order to find indvidual bulbs, which causes a short but noticeable delay. To avoid device discovery, you can either instantiate Light objects directly using their MAC address and IP address (which you can learn by running `examples/hello_world.py`), or you can use the broadcast methods provided in the LifxLAN API. In the examples folder, `broadcast_on.py`, `broadcast_off.py`, and `broadcast_color.py` will allow you to send commands to all lights quickly from the command line without doing device discovery.

## Overview

You can do several things with this library:

* Control LIFX devices using the package's high-level API (see the `examples` folder and the following API sections).
* Build your own high-level API on top of the low-level networking messages.
* Build virtual LIFX devices in software (think adapters for Philips Hue bulbs, Wemo, etc).

#### High-Level API:

* **lifxlan.py** - Provides the LifxLAN API, and low-level API for sending broadcast LIFX packets to the LAN.
* **device.py** - Provides the Device API, and low-level API for sending unicast LIFX packets to a Device.
* **light.py** - Provides the Light API. Subclass of Device.

##### LifxLAN API

You can create a LifxLAN object to represent the local network:

```
lan = LifxLAN()
```

LifxLAN objects have the following methods:

```
# power can be "on"/"off", True/False, 0/1, or 0/65535
# color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
# duration is the transition time in milliseconds
# rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
# NOTE: rapid is meant for super-fast light shows with lots of changes. You should't need it for normal use. 
# arguments in [square brackets] are optional

get_lights()                                            # returns list of Light objects
set_power_all_lights(power, [duration], [rapid])        # set power for all lights on LAN
set_color_all_lights_color(color, [duration], [rapid])  # set color for all lights on LAN
get_power_all_lights()                                  # returns dict of Light, power pairs
get_color_all_lights()                                  # returns dict of Light, color pairs
```

##### Device API

In keeping with the LIFX protocol, all lights are devices, and so support the following methods:

```
# label is a string, 32 char max
# power can be "on"/"off", True/False, 0/1, or 0/65535
# rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
# NOTE: rapid is meant for super-fast light shows with lots of changes. You should't need it for normal use. 
# arguments in [square brackets] are optional

set_label(label)            
set_power(power, [rapid])            
get_mac_addr()
get_ip_addr()
get_service()                       # returns int, 1 = UDP
get_port()                          
get_label()         
get_power()                         # returns 0 for off, 65535 for on
get_host_firmware_tuple()           # returns (build_timestamp (in nanoseconds), version)
get_host_firmware_build_timestamp()
get_host_firmware_version()
get_wifi_info_tuple()               # returns (wifi_signal_mw, wifi_tx_bytes, wifi_rx_bytes)
get_wifi_signal_mw()
get_wifi_tx_bytes()
get_wifi_rx_bytes()         
get_wifi_firmware_tuple()           # returns (build_timestamp (in nanoseconds), version)
get_wifi_firmware_build_timestamp() 
get_wifi_firmware_version()
get_version_tuple()                 # returns (vendor, product, version)
get_location()                      # Returns location id (bytearray length 16)
get_location_tuple()                # Returns a tuple of location(bytearray lenght 16), location_label(string), and location_updated_at(unsigned 64 bit epoch timestamp)
get_location_label()                # Returns location_label string
get_location_updated_at             # Returns location_updated_at unsigned 64 bit int -> epoch timestamp
get_group()                         # Returns group id (bytearray length 16)
get_group_tuple()                   # Returns a tuple of group(bytearray lenght 16), group_label(string), and group_updated_at(unsigned 64 bit epoch timestamp)
get_group_label()                   # Returns group_label(string)
get_group_updated_at                # Returns group_updated_at unsigned 64 bit int -> epoch timestamp
get_vendor()
get_product()
get_version()
get_info_tuple()                    # returns (time (current timestamp in ns), uptime (in ns), downtime (in ns, +/- 5 seconds))
get_time()
get_uptime()
get_downtime()
```

##### Light API

You can get Light objects automatically though LAN-based discovery (takes a few seconds), or by creating Light objects using a known MAC address and IP address:

```
lights = lan.get_lights()
light = Light("12:34:56:78:9a:bc", "192.168.1.42")
```

The Light API provides everything in the Device API, as well as:

```
# arguments in [square brackets] are optional
# power can be "on"/"off", True/False, 0/1, or 0/65535
# color is a HSBK list of values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
# duration is the transition time in milliseconds
# rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
# is_transient is 1/0. If 1, return to the original color after the specified number of cycles. If 0, set light to specified color
# period is the length of one cycle in milliseconds
# cycles is the number of times to repeat the waveform
# duty_cycle is an integer between -32768 and 32767. Its effect is most obvious with the Pulse waveform 
#     set duty_cycle to 0 to spend an equal amount of time on the original color and the new color
#     set duty_cycle to positive to spend more time on the original color
#     set duty_cycle to negative to spend more time on the new color
# waveform can be 0 = Saw, 1 = Sine, 2 = HalfSine, 3 = Triangle, 4 = Pulse (strobe)

# NOTE: rapid is meant for super-fast light shows with lots of changes. You should't need it for normal use.
# NOTE: currently is_transient=1 results in bulbs staying on the last color of the waveform instead of original color. This is a LIFX problem.

set_power(power, [duration], [rapid])   
set_color(color, [duration], [rapid])                                   
set_waveform(is_transient, color, period, cycles, duty_cycle, waveform)     # currently experimental, undocumented in official protocol
get_power()                                                                 # returns 0 or 65535
get_color()                                                                 # returns color (HSBK list)
```

The Light API also provides macros for basic colors, like RED, BLUE, GREEN, etc. Setting colors is as easy as `mybulb.set_color(BLUE)`. See light.py for complete list of color macros.

#### LIFX LAN Protocol Implementation:

The LIFX LAN protocol V2 specification is officially documented [here](https://github.com/LIFX/lifx-protocol-docs). In lifxlan, you can see the underlying stream of packets being sent and received at any time by initializing the LifxLAN object with the verbose flag set: `lifx = LifxLAN(verbose = True)`. (See `examples/verbose_lan.py`.)

The files that deal with LIFX packet construction and representation are:

* **message.py** -  Defines the message fields and the basic packet structure.
* **msgtypes.py** - Provides subclasses for each LIFX message type, along with their payload constructors.
* **unpack.py** - Creates a LIFX message object from a string of binary data (crucial for receiving messages).

Happy hacking!
