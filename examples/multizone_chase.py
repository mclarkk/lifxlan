#!/usr/bin/env python
from lifxlan import *
from array import *
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
    lifx = LifxLAN(num_lights,False)

    # get devices
    devices = lifx.get_lights()
    bulb = devices[0]
    print("Selected {}".format(bulb.get_label()))

    speed = 0.1
    color1 = RED
    color2 = GREEN
    size = 12 #WIDTH

    for b in devices:
        print(b.get_label())
        if "strip" in b.get_label().lower():
            strip =  MultiZoneLight(b.mac_addr, b.ip_addr)
            color_zones = strip.get_color_zones()
            zone_count = len(color_zones) #autodetect zones
            size = size - 1 #0 based
            zone_count = zone_count - 1
            start = 0
            while True:
                strip.set_zone_color(0, zone_count, color1, 0, True, 0) #queue command
                if start > zone_count-size:
                    end = size - (zone_count - start) - 1
                    strip.set_zone_color(0, end, color2, 0, True, 0)#queue command
                strip.set_zone_color(start, start+size, color2,0,True,1) #execute command

                start += 1
                if start > zone_count:
                    start = 0
                sleep(speed)

if __name__=="__main__":
    main()
