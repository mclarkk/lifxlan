#!/usr/bin/env python

from lifxlan import *
import sys

colors = {
    "red": RED, 
    "orange": ORANGE, 
    "yellow": YELLOW, 
    "green": GREEN, 
    "cyan": CYAN, 
    "blue": BLUE, 
    "purple": PURPLE, 
    "pink": PINK, 
    "white": WHITE, 
    "cold_white": COLD_WHTE, 
    "warm_white": WARM_WHITE, 
    "gold": GOLD
}
error_message = """Usage:

   python set_color_all.py blue
   python set_color_all.py 43634 65535 65535 3500

The four numbers are HSBK values: Hue (0-65535), Saturation (0-65535), Brightness (0-65535), Kelvin (2500-9000).
See get_colors_all.py to read the current HSBK values from your lights.

The available predefined colors are:
""" + ", ".join(colors.keys())

lifxlan = LifxLAN()

color = None
if len(sys.argv) == 2:
    if sys.argv[1].lower() not in colors:
        print(error_message)
        sys.exit()
    else:
        color = colors[sys.argv[1].lower()]
elif len(sys.argv) == 5:
    color = []
    for (i, value) in enumerate(sys.argv[1:]):
        try:
            value = int(value)
        except:
            print("Problem with {}.".format(value))
            print(error_message)
            sys.exit()
        if i == 3 and (value < 2500 or value > 9000):
            print("{} out of valid range.".format(value))
            print(error_message)
            sys.exit()
        elif value < 0 or value > 65535:
            print("{} out of valid range.".format(value))
            print(error_message)
            sys.exit()
        color.append(value)
else:
    print(error_message)
    sys.exit()

lifxlan.set_color_all_lights(color, rapid=True)

