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
    devices = lifx.get_lights()
    strip = None
    for d in devices:
        print(d.get_label())
        if "strip" in d.get_label().lower():
            strip =  MultiZoneLight(d.mac_addr, d.ip_addr)



    if strip != None:
        print("Selecting " + strip.get_label())
        #%h, s, v, k = l.get_color_zones()
        all_zones = []
        for i in range(4):
            zones = strip.get_color_zones(0+(i*8),7+(i*8))
            all_zones += zones
        #print(all_zones)
        original_zones = deepcopy(all_zones)
        zone_buff = all_zones

        ignore = [-1]

        try:
            while True:
                for i in range(12):
                    z = -1
                    while z in ignore:
                        z = randrange(0,31)
                    ignore.append(z)
                    h, s, v, k = zone_buff[z]
                    zone_buff[z] = h, s, 2000, k
                    strip.set_zone_color(z, z, [h, s, 40000, k], 500, True)
                    sleep(0.01)
                #l.set_zone_colors(zone_buff, 2000, True)
                for i in range(12):
                    z = -1
                    while z in ignore:
                        z = randrange(0,31)
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
