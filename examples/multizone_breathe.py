from lifxlan import *
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
    strip = None
    for d in devices:
        print(d.get_label())
        if "strip" in d.get_label().lower():
            strip =  MultiZoneLight(d.mac_addr, d.ip_addr)



    if strip != None:
        print("Selecting " + strip.get_label())
        all_zones = []
        for i in range(4):
            zones = strip.get_color_zones(0+(i*8),7+(i*8))
            all_zones += zones
        original_zones = all_zones
        dim_zones = []
        bright_zones = []
        for [h,s,v,k] in all_zones:
            dim_zones.append((h,s,20000,k))
            bright_zones.append((h,s,65535,k))

        try:
            while True:
                strip.set_zone_colors(bright_zones, 2000, True)
                sleep(2)
                strip.set_zone_colors(dim_zones, 2000, True)
                sleep(2)
        except KeyboardInterrupt:
            strip.set_zone_colors(original_zones, 1000, True)
    else:
        print("No strips detected.")

if __name__=="__main__":
    main()
