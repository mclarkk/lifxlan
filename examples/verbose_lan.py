#!/usr/bin/env python
# coding=utf-8

import sys

from lifxlan import LifxLAN


def main():
    num_devices = None
    if len(sys.argv) != 2:
        print(
            "\nDiscovery will go much faster if you provide the number of devices on your LAN:"
        )
        print(f"  python {sys.argv[0]} <number of devices on LAN>\n")
    else:
        num_devices = int(sys.argv[1])

    # instantiate LifxLAN client, num_devices may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of devices at all.
    # lifx = LifxLAN() works just as well. Knowing the number of devices in advance
    # simply makes initial device discovery faster.
    print("Discovering devices...")
    lifx = LifxLAN(num_devices, verbose=True)

    # get devices
    devices = lifx.get_devices()
    print("Found Devices:")
    for device in devices:
        label = device.get_label()
        print(label)


if __name__ == "__main__":
    main()
