#!/usr/bin/env python
# coding=utf-8
import sys
from copy import copy
from time import sleep, time

from lifxlan import LifxLAN


def main():
    num_lights = None
    if len(sys.argv) != 2:
        print(
            "\nDiscovery will go much faster if you provide the number of lights on your LAN:"
        )
        print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
    else:
        num_lights = int(sys.argv[1])

    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.
    lifx = LifxLAN(num_lights)

    # test power control
    print("Discovering lights...")
    original_powers = lifx.get_power_all_lights()
    original_colors = lifx.get_color_all_lights()

    half_period_ms = 2500
    duration_mins = 20
    duration_secs = duration_mins * 60
    print("Breathing...")
    try:
        start_time = time()
        while True:
            for bulb in original_colors:
                color = original_colors[bulb]
                dim = list(copy(color))
                dim[2] = 1900
                bulb.set_color(dim, half_period_ms, rapid=True)
            sleep(half_period_ms / 1000.0)
            for bulb in original_colors:
                color = original_colors[bulb]
                bulb.set_color(color, half_period_ms, rapid=True)
            sleep(half_period_ms / 1000.0)
            if time() - start_time > duration_secs:
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Restoring original color to all lights...")
        for light in original_colors:
            color = original_colors[light]
            light.set_color(color)

        print("Restoring original power to all lights...")
        for light in original_powers:
            power = original_powers[light]
            light.set_power(power)


if __name__ == "__main__":
    main()
