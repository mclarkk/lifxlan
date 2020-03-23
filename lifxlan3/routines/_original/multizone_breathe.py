#!/usr/bin/env python
# coding=utf-8

import sys
from time import sleep

from lifxlan3 import LifxLAN


def main():
    num_lights = None
    if len(sys.argv) != 2:
        print("\nDiscovery will go much faster if you provide the number of lights on your LAN:")
        print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
    else:
        num_lights = int(sys.argv[1])

    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.
    print("Discovering lights...")
    lifx = LifxLAN(num_lights, False)

    # get devices
    multizone_lights = lifx.multizone_lights

    if len(multizone_lights) > 0:
        strip = multizone_lights[0]
        print("Selecting " + strip.label)
        all_zones = strip.get_color_zones()
        original_zones = all_zones
        dim_zones = []
        bright_zones = []
        for [h, s, v, k] in all_zones:
            dim_zones.append((h, s, 20000, k))
            bright_zones.append((h, s, 65535, k))

        try:
            print("Breathing...")
            while True:
                strip.set_zone_colors(bright_zones, 2000, True)
                sleep(2)
                strip.set_zone_colors(dim_zones, 2000, True)
                sleep(2)
        except KeyboardInterrupt:
            strip.set_zone_colors(original_zones, 1000, True)
    else:
        print("No lights with Multizone capability detected.")


if __name__ == "__main__":
    main()
