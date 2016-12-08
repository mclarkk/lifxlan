#!/usr/bin/env python
from lifxlan import *
import sys
from time import sleep

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

    # get devices
    devices = lifx.get_lights()
    bulb = devices[0]
    print("Selected {}".format(bulb.get_label()))

    # get original state
    print("Turning on all lights...")
    original_power = bulb.get_power()
    original_color = bulb.get_color()
    bulb.set_power("on")

    sleep(1) # for looks

    print("Flashy fast rainbow")
    rainbow(bulb, 0.1)

    print("Smooth slow rainbow")
    rainbow(bulb, 1, smooth=True)

    print("Restoring original power and color...")
    # restore original power
    bulb.set_power(original_power)
    # restore original color
    sleep(0.5) # for looks
    bulb.set_color(original_color)

def rainbow(bulb, duration_secs=0.5, smooth=False):
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
    transition_time_ms = duration_secs*1000 if smooth else 0
    rapid = True if duration_secs < 1 else False
    for color in colors:
        bulb.set_color(color, transition_time_ms, rapid)
        sleep(duration_secs)

if __name__=="__main__":
    main()
