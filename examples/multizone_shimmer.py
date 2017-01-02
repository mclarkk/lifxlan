from lifxlan import *
from time import sleep
from random import randrange
from copy import deepcopy

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
        print("Selecting " + strip.get_label())
        all_zones = strip.get_color_zones()
        original_zones = deepcopy(all_zones)
        zone_buff = all_zones

        ignore = [-1]

        try:
            while True:
                for i in range(12):
                    z = -1
                    while z in ignore:
                        z = randrange(0,len(zone_buff))
                    ignore.append(z)
                    h, s, v, k = zone_buff[z]
                    zone_buff[z] = h, s, 2000, k
                    strip.set_zone_color(z, z, [h, s, 40000, k], 500, True)
                    sleep(0.01)
                #l.set_zone_colors(zone_buff, 2000, True)
                for i in range(12):
                    z = -1
                    while z in ignore:
                        z = randrange(0,len(zone_buff))
                    ignore.append(z)
                    h, s, v, k = zone_buff[z]
                    zone_buff[z] = h, s, 65535, k
                    strip.set_zone_color(z, z, [h, s, 65535, k], 500, True)
                    sleep(0.01)
                #l.set_zone_colors(zone_buff, 2000, True)
                #sleep(0.25)
                ignore = [-1]
        except KeyboardInterrupt:
            strip.set_zone_colors(original_zones, 1000, True)

if __name__=="__main__":
    main()
