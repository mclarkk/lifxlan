#!/usr/bin/env python
# coding=utf-8
import sys
from time import sleep

from lifxlan import LifxLAN, Colors

BLINK_ALL = True


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
    lifx = LifxLAN()

    # get devices
    devices = lifx.color_lights
    if not BLINK_ALL:
        devices = devices['master 2']
    print("Selected {}".format(devices.label))

    interval_secs, num_cycles = .1, 12
    # get original state
    with devices.reset_to_orig(1000):
        devices.turn_on()

        sleep(0.2)  # to look pretty

        print("Toggling power...")
        toggle_device_power(devices, interval_secs, num_cycles)

        print("Toggling color...")
        toggle_light_color(devices, interval_secs, num_cycles)


def toggle_device_power(device, interval=0.5, num_cycles=3):  # TEST
    with device.reset_to_orig():
        device.set_power("off")
        for i in range(num_cycles):
            for power in range(2):
                device.set_power(power)
                sleep(interval)


def toggle_light_color(light, interval=0.5, num_cycles=3):
    with light.reset_to_orig():
        for i in range(num_cycles):
            for c in Colors.YALE_BLUE.get_complements(90)[:4]:
                light.set_color(c)
                sleep(interval)


if __name__ == "__main__":
    main()
