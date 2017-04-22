#!/usr/bin/env python
# coding=utf-8
import sys
from copy import deepcopy
from time import sleep

from lifxlan import GREEN, LifxLAN, RED


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
    multizone_lights = lifx.get_multizone_lights()

    if len(multizone_lights) > 0:
        strip = multizone_lights[0]
        print("Selected {}".format(strip.get_label()))

        all_zones = strip.get_color_zones()
        original_zones = deepcopy(all_zones)
        zone_count = len(all_zones)

        delay = 0.06
        snake_color = RED
        background_color = GREEN
        snake_size = zone_count/2 # length of snake in zones

        tail = 0
        head = snake_size - 1

        try:
            while True:
                # Case 1: Snake hasn't wrapped around yet
                if head > tail:
                    if tail > 0:
                        strip.set_zone_color(0, tail-1, background_color, 0, True, 0)
                    strip.set_zone_color(tail, head, snake_color, 0, True, 0)
                    if head < zone_count - 1:
                        strip.set_zone_color(head+1, zone_count-1, background_color, 0, True, 1)

                # Case 2: Snake has started to wrap around
                else:
                    if head > 0:
                        strip.set_zone_color(0, head-1, snake_color, 0, True, 0)
                    strip.set_zone_color(head, tail, background_color, 0, True, 0)
                    if tail < zone_count - 1:
                        strip.set_zone_color(tail+1, zone_count-1, snake_color, 0, True, 1)

                # update indices for the snake's head and tail
                tail = (tail+1) % zone_count
                head = (head+1) % zone_count

                sleep(delay)
        except KeyboardInterrupt:
            strip.set_zone_colors(original_zones, 500, True)

if __name__=="__main__":
    main()
