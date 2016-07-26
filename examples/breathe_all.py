#!/usr/bin/env python
from lifxlan import *
import sys
from copy import copy
from time import sleep, time

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
    bulbs = lifx.get_lights()

    # test power control
    print("Discovering lights...")
    original_powers = lifx.get_power_all_lights()
    original_colors = lifx.get_color_all_lights()
    print original_colors


    half_period_ms = 2500
    duration_mins = 20
    duration_secs = duration_mins*60
    print("Breathing...")
    try:    
        start_time = time()
        while True:
            for bulb, color in original_colors:
                dim = list(copy(color))
                half_bright = int(dim[2]/2)
                dim[2] = half_bright if half_bright >= 1900 else 1900
                bulb.set_color(dim, half_period_ms, rapid=True)
                sleep(half_period_ms/1000.0)
            for bulb, color in original_colors:
                bulb.set_color(color, half_period_ms, rapid=True)
                sleep(half_period_ms/1000.0)
            if time() - start_time > duration_secs:
                raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Restoring original color to all lights...")
        for light, color in original_colors:
            light.set_color(color)

        print("Restoring original power to all lights...")
        for light, power in original_powers:
            light.set_power(power)

if __name__=="__main__":
    main()
