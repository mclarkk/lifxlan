#!/usr/bin/env python
from lifxlan import *
import sys

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
    lifx = LifxLAN(num_lights)

    # test power control
    print("Discovering lights...")
    original_powers = lifx.get_power_all_lights()

    print("Turning lights on...")
    lifx.set_power_all_lights("on")

    sleep(0.2)

    print("Toggling power of all lights...")
    toggle_all_lights_power(lifx, 0.2)

    print("Restoring power to all lights...")
    for light, power in original_powers:
        light.set_power(power)


    # test color control
    original_colors = lifx.get_color_all_lights()

    print("Turning lights on...")
    lifx.set_power_all_lights("on")

    sleep(1)

    print("Toggling color of all lights quickly...")
    toggle_all_lights_color(lifx, 0.2)

    print("Toggling color of all lights slowly...")
    toggle_all_lights_color(lifx, 1)

    print("Restoring original color to all lights...")
    for light, color in original_colors:
        light.set_color(color)

    sleep(1)

    print("Restoring original power to all lights...")
    for light, power in original_powers:
        light.set_power(power)




def toggle_all_lights_power(lan, interval=0.5, num_cycles=3): #TEST
    lan.set_power_all_lights("off")
    rapid = True if interval < 1 else False
    for i in range(num_cycles):
        lan.set_power_all_lights("on", rapid)
        sleep(interval)
        lan.set_power_all_lights("off", rapid)
        sleep(interval)

def toggle_all_lights_color(lan, interval=0.5, num_cycles=3):
    rapid = True if interval < 1 else False
    for i in range(num_cycles):
        lan.set_color_all_lights(BLUE, rapid=rapid)
        sleep(interval)
        lan.set_color_all_lights(GREEN, rapid=rapid)
        sleep(interval)

if __name__=="__main__":
    main()
