import lifxlan


def __main():
    lan = lifxlan.LifxLAN()
    l = lan.lights[0]
    print(len(lan.lights))
    print(l.color)
    print(l.power_level)


if __name__ == '__main__':
    __main()
