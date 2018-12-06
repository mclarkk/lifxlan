#!/usr/bin/env python
# coding=utf-8
import sys
from time import sleep

from lifxlan import LifxLAN, Colors


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
    lifx = LifxLAN(num_lights)
    lifx = lifx['master']

    with lifx.reset_to_orig(2000):

        print("Turning on all lights...")
        lifx.turn_on()
        sleep(1)

        print("Flashy fast rainbow")
        rainbow(lifx, 0.3)

        print("Smooth slow rainbow")
        rainbow(lifx, 20, smooth=True)

    print("Restoring original colors/powers to all lights...")


def rainbow(lan, duration_secs=0.5, smooth=False):
    colors = Colors.RAINBOW
    transition_time_ms = duration_secs * 1000 if smooth else 0
    rapid = duration_secs < 1
    for color in colors:
        lan.set_color(color, transition_time_ms, rapid)
        sleep(duration_secs)


if __name__ == "__main__":
    main()
