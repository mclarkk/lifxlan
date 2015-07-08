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
    lifx = LifxLAN(num_lights, verbose=True)

    # get devices
    print("Discovering lights...")
    devices = lifx.get_lights()
    labels = []
    for device in devices:
        labels.append(device.get_label())
    print("Found Bulbs:")
    for label in labels:
        print("  " + label)

if __name__ == "__main__":
    main()