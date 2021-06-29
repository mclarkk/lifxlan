# lifxlan

**lifxlan** is a Python 3 module for locally controlling LIFX devices (such as lightbulbs) over a LAN. It implements the [LIFX LAN Protocol](https://lan.developer.lifx.com/) specification. Supports white, color, multizone (LIFX Z, LIFX Beam), infrared (LIFX+), and chain (LIFX Tile) capabilities. Also supports group-based control of arbitrary sets of lights. Supports Unicode characters in names, groups, and locations.

## How to Install

To get the latest stable release:

`sudo pip install lifxlan`

However, to be guaranteed to get the most recent features and fixes you can install from source with:

`sudo python setup.py install`

## Run

See the `examples` folder for example scripts that use **lifxlan**.

To be as generic as possible, the examples use automatic device discovery to find individual bulbs, which causes a short but noticeable delay. To avoid device discovery, you can either instantiate Light objects directly using their MAC address and IP address (which you can learn by running `examples/hello_world.py`), or you can use the broadcast methods provided in the LifxLAN API. In the examples folder, `broadcast_on.py`, `broadcast_off.py`, and `broadcast_color.py` will allow you to send commands to all lights quickly from the command line without doing device discovery.

## Overview

You can do several things with this library:

- Control LIFX devices using the package's high-level API (see the `examples` folder and the following API sections).
- Build your own high-level API on top of the low-level networking messages.
- Build virtual LIFX devices in software (think adapters for Philips Hue bulbs, etc).

#### High-Level API:

- **lifxlan.py** - Provides the LifxLAN API, and low-level API for sending broadcast LIFX packets to the LAN.
- **device.py** - Provides the Device API, and low-level API for sending unicast LIFX packets to a Device.
- **light.py** - Provides the Light API. Subclass of Device.
- **multizonelight.py** - Provides the MultiZoneLight API. Subclass of Light.
- **tilechain.py** - Provides the TileChain API. Subclass of Light.
- **group.py** - Provides the Group API. Allows you to perform synchronized actions on groups of devices.

##### LifxLAN API

You can create a LifxLAN object to represent the local network:

```
lan = LifxLAN()
lan = LifxLAN(num_lights)   #this will make discovery go faster if all lights are responsive
```

LifxLAN objects have the following methods:

```
# power can be "on"/"off", True/False, 0/1, or 0/65535
# color is a list of HSBK values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
# duration is the transition time in milliseconds
# rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
# NOTE: rapid is meant for super-fast light shows with lots of changes. You should't need it for normal use.
# arguments in [square brackets] are optional
# name is the string label for the light, such as "Right Lamp"
# names is a list of name strings, such as ["Left Lamp", "Right Lamp"]
# group is a string label for a group, such as "Living Room"
# location is the string label for a location, such as "My Home"

get_lights()                                                                                 # returns list of Light objects
get_color_lights()                                                                           # returns list of Light objects that support color functionality
get_infrared_lights()                                                                        # returns list of Light objects that support infrared functionality
get_multizone_lights()                                                                       # returns list of MultiZoneLight objects that support multizone functionality
get_tilechain_lights()                                                                       # returns a list of TileChain objects that support chain functionality
get_device_by_name(name)                                                                     # returns a Device object (instantiated as the most specific Device subclass possible, such as MultiZoneLight)
get_devices_by_name(names)                                                                   # returns a Group object
get_devices_by_group(group)                                                                  # returns a Group object
get_devices_by_location(location)                                                            # returns a Group object
set_power_all_lights(power, [duration], [rapid])                                             # set power for all lights on LAN
set_color_all_lights(color, [duration], [rapid])                                             # set color for all lights on LAN
set_waveform_all_lights(is_transient, color, period, cycles, duty_cycle, waveform, [rapid])  # see the Light API for more details
get_power_all_lights()                                                                       # returns dict of Light, power pairs
get_color_all_lights()                                                                       # returns dict of Light, color pairs
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
is_light()                          # returns True if device is some kind of light product
supports_color()                    # returns True if product features include color
supports_temperature()              # returns True if product features include white color temperature
supports_multizone()                # returns True if product features include multizone functionality
supports_infrared()                 # returns True if product features include infrared functionality
```

##### Light API

You can get Light objects automatically though LAN-based discovery (takes a few seconds), or by creating Light objects using a known MAC address and IP address:

```
lights = lan.get_lights()                              # Option 1: Discovery
light = Light("12:34:56:78:9a:bc", "192.168.1.42")     # Option 2: Direct
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
# infrared_brightness (0-65535) - is the maximum infrared brightness when the lamp automatically turns on infrared (0 = off)

# NOTE: rapid is meant for super-fast light shows with lots of changes. You should't need it for normal use.

set_power(power, [duration], [rapid])
set_color(color, [duration], [rapid])
set_waveform(is_transient, color, period, cycles, duty_cycle, waveform)
get_power()                                                                 # returns 0 or 65535
get_color()                                                                 # returns color (HSBK list)
get_infrared()                                                              # returns infrared brightness (0 to 65535), or None if infrared is not supported
set_infrared(infrared_brightness)
```

The Light API also provides macros for basic colors, like RED, BLUE, GREEN, etc. Setting colors is as easy as `mybulb.set_color(BLUE)`. See light.py for complete list of color macros.

Finally, you can set parts of the color individually using the following four methods. However, the bulbs must receive all four values in each SetColor message. That means that using one of the following methods is always slower than using set_color(color) above because it will have to call get_color() first to get the other three values.

```
set_hue(hue, [duration], [rapid])                  # hue in range [0-65535]
set_brightness(brightness, [duration], [rapid])    # brightness in range [0-65535]
set_saturation(saturation, [duration], [rapid])    # saturation in range [0-65535]
set_colortemp(kelvin, [duration], [rapid])         # kelvin in range [2500-9000]
```

##### MultiZoneLight API

Lights with MultiZone capability, such as the LIFX Z, have all the same methods as the Light API, and also add the following:

```
# start and end refer to zone indices (inclusive).
# duration is the transition time in milliseconds
# rapid is True/False. True means there is no guarantee that the bulb will receive your message.
# apply is 1/0. If 0, queue up the change until a packet with apply=1 comes by, then apply all queued changes.
# effect_type is 0 for None, 1 for Move

get_color_zones([start], [end])                                    # returns a list of [H,S,V,K] colors, one for each zone. Length of the list is the number of zones.
set_zone_color(start, end, color, [duration], [rapid], [apply])    # indices are inclusive and zero-indexed
set_zone_colors(colors, [duration], [rapid])                       # colors is a list of [H,S,V,K] colors, which will get applied to the zones in order. This makes it possible to restore the original colors easily after a display.
get_multizone_effect()                                             # returns current firmware effect status
set_multizone_effect([effect_type], [speed], [duration], [instanceid], [parameters], [rapid]) # starts the firmware effect sequence
```

The LIFX Z can be instantiated as either a Light or MultiZoneLight object, but to use the MultiZone API you'll need to instantiate it as a MultiZoneLight. Just like with more generic Light objects, you can instantiate a MultiZoneLight directly with `light = MultiZoneLight("12:34:56:78:9a:bc", "192.168.1.23")`. You can also get a list of all MultiZone lights using `lights = lan.get_multizone_lights()`, where lan is a LifxLAN object.

##### TileChain API

TileChain lights, such as the LIFX Tile, have all the same methods as the Light API, and also add the following:

```
# refresh_cache is a binary value. If True, send the query directly to the light to get the answer, and update the locally stored information (slower). If False, return the locally stored answer from a previous query (faster). Should almost always be False, unless the configuration of the Tiles is expected to change while the program is running (an unusual concern for most programs).
# tile_count is the number of tiles on which to replicate the command, starting from the start_index tile.
# x, y, and width will probably not be used. They allow the user to specify a rectangle of LEDs on the specified tile. The (x, y) coordinate gives the starting LED, and the width gives the width of the desired rectangle. The default values of these ((0, 0) and 8) specify the whole tile, and will probably not need to be changed.
# colors is a list of 64 HSVK tuples.
# tilechain_colors is a list of tile_count x 64 HSVK tuples, used for getting and setting the entire TileChain's colors at once.
# hsvk_matrix is a 2D list of HSVK color tuples with canvas_dimensions rows and cols. The canvas_dimensions will depend on the configuration of the tiles. The canvas can be thought of as the rectangular bounding box around the entire TileChain, where each pixel is an LED.
# effect_type is 0 for None, 2 for Morph and 3 for Flame. 1 is Reserved.

get_tile_info([refresh_cache])                                  # returns a list of Tile objects
get_tile_count([refresh_cache])                                 # returns the number of Tiles in the TileChain light
get_tile_colors(start_index, [tile_count], [x], [y], [width])   # returns colors for the specified tile(s).
set_tile_colors(start_index, colors, [duration], [tile_count], [x], [y], [width], [rapid]) # sets the colors on the specified tile(s). For tile_count > 1, the colors will be duplicated.
get_tilechain_colors()                                          # returns tilechain_colors
set_tilechain_colors(tilechain_colors, [duration], [rapid])     # sets all the colors on the whole TileChain
project_matrix(hsvk_matrix, [duration], [rapid])                # projects the given matrix of colors onto the TileChain.
get_canvas_dimensions([refresh_cache])                          # returns (x, y), representing the rows and columns of the bounding box around the entire TileChain, where each element is an individual LED position.
get_tile_effect()                                               # returns current firmware effect status
set_tile_effect([effect_type], [speed], [duration], [palette], [instanceid], [parameters], [rapid]) # starts the firmware effect sequence
```

Here are some other available methods that you are much less likely to use:

```
# x and y below are in units of tile length, not LED rows/cols. In other words, the x and y below are not the same as the x and y above.

recenter_coordinates()                  # This will permanently shift all the tile coordinates so that they are centered around a tile at (0, 0). Sometimes the app will result in a particular axis being off (e.g., the origin tile is (0, -0.5), so all the tile coordinates are shifted by -0.5). This method isn't necessary for any functionality, but makes the tile_info a little more human-readable.
set_tile_coordinates(tile_index, x, y)  # Permanently sets the specified tile's coordinates to x and y (in tile length units) relative to the central tile. Tile coordinates are generally set through the LIFX app, and it is unlikely you will need to ever use this method unless you're doing something pretty weird. (If so, drop me a line!)
get_tile_map([refresh_cache])           # Returns a 2D list with canvas_dimensions rows and cols where each element contains either a (tile_index, color_index) tuple or 0. This maps a pixel on the canvas to the tile number and LED number on that tile that the pixel corresponds to, or 0 if there is no tile in that location.
```

A LIFX Tile light can be instantiated as either a Light or TileChain object, but to use the TileChain API you'll need to instantiate it as a TileChain. Just like with more generic Light objects, you can instantiate a TileChain directly with `light = TileChain("12:34:56:78:9a:bc", "192.168.1.23")`. You can also get a list of all tilechain lights using `lights = lan.get_tilechain_lights()`, where lan is a LifxLAN object.

##### Group API

A Group is a collection of devices. Under the covers, a Group is just a list of device objects (like Devices, Lights, MultiZoneLights) and a set of functions that send multi-threaded commands to the applicable devices in the group. The multi-threading allows changes to be made more or less simultaneously. At the very least, it is certainly faster than if you looped through each individual light one at a time. You can get a Group by group, location, or device names via the LifxLAN API. However, you can also instantiate a Group with any arbitrary list of device objects. Here are some ways to create groups:

```
# The following methods use discovery
lan = LifxLAN()
g = lan.get_devices_by_name(["Left Lamp", "Right Lamp"])
g = lan.get_devices_by_group("Living Room")
g = lan.get_devices_by_location("My Home")

# This method is fastest
right = Light("12:34:56:78:9a:bc", "192.168.0.2")
left = Light("cb:a9:87:65:43:21", "192.168.0.3")
g = Group([right, left])
```

Almost all of the Group API methods are commands. Commands will only be sent to the devices in the group that support that capability. If you want to get state information from the devices, you will need to access the list of devices and call their get methods directly.

```
# device_object is a Device or any of its subclasses like Light and MultiZoneLight.
# device_name is a string name of a device, like "Right Lamp"
# power can be "on"/"off", True/False, 0/1, or 0/65535
# color is a HSBK list of values: [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
# infrared_brightness is an integer between 0 and 65535.
# duration is the transition time in milliseconds
# rapid is True/False. If True, don't wait for successful confirmation, just send multiple packets and move on
# start and end refer to zone indices (inclusive).
# apply is 1/0. If 0, queue up the change until a packet with apply=1 comes by, then apply all queued changes.

add_device(device_object)
remove_device(device_object)
remove_device_by_name(device_name)
get_device_list()
set_power(power, [duration], [rapid])
set_color(color, [duration], [rapid])
set_hue(hue, [duration], [rapid])
set_brightness(brightness, [duration], [rapid])
set_saturation(saturation, [duration], [rapid])
set_colortemp(kelvin, [duration], [rapid])
set_infrared(infrared_brightness)
set_zone_color(start, end, color, [duration], [rapid], [apply])
set_zone_colors(colors, [duration], [rapid])
```

#### LIFX LAN Protocol Implementation:

The LIFX LAN protocol specification is officially documented [here](https://lan.developer.lifx.com/). In lifxlan, you can see the underlying stream of packets being sent and received at any time by initializing the LifxLAN object with the verbose flag set: `lifx = LifxLAN(verbose = True)`. (See `examples/verbose_lan.py`.) You can also set the verbose flag if creating a Light or MultiZoneLight object directly.

The files that deal with LIFX packet construction and representation are:

- **message.py** - Defines the message fields and the basic packet structure.
- **msgtypes.py** - Provides subclasses for each LIFX message type, along with their payload constructors.
- **unpack.py** - Creates a LIFX message object from a string of binary data (crucial for receiving messages).

Happy hacking!
