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

    # get devices
    devices = lifx.get_lights()
    bulb = devices[0]
    print("Selected {}".format(bulb.get_label()))

    # get color
    original_color = bulb.get_color()

    print("Flashy fast rainbow")
    rainbow(bulb, 0.1)

    print("Smooth slow rainbow")
    rainbow(bulb, 1, smooth=True)

    # restore original color
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