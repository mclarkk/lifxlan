import lifxlan


def __main():
    lan = lifxlan.LifxLAN(100)
    lan.discover_devices()
    l = lan.lights[0]
    print(l.color)
    print(l.get_power())


if __name__ == '__main__':
    __main()
