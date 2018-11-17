import lifxlan


def __main():
    lan = lifxlan.LifxLAN(100)
    lan.discover_devices()
    d = lan.devices[0]
    print(len(lan.devices))
    print(lan.lights)


if __name__ == '__main__':
    __main()
