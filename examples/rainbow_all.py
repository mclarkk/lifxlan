from lifxlan import *
import sys

def main():
    num_lights = None
    if len(sys.argv) != 2:
        print("\nDiscovery will go much faster if you provide the number of lights on your LAN:")
        print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
    else:
        num_lights = int(sys.argv[1])

    # instantiate LifxLAN client
    print("Discovering lights...")
    lifx = LifxLAN(num_lights)

    original_colors = lifx.get_color_all_lights()

    print("Flashy fast rainbow")
    rainbow(lifx, 0.1)

    print("Smooth slow rainbow")
    rainbow(lifx, 1, smooth=True)

    # restore original color
    print("Restoring original colors...")
    for bulb, color in original_colors:
        bulb.set_color(color)

def rainbow(lan, duration_secs=0.5, smooth=False):
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
    transition_time_ms = duration_secs*1000 if smooth else 0
    rapid = True if duration_secs < 1 else False
    for color in colors:
        lan.set_color_all_lights(color, transition_time_ms, rapid)
        sleep(duration_secs)

if __name__=="__main__":
    main()