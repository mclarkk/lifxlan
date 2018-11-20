import lifxlan
from lifxlan import Color


def __main():
    lan = lifxlan.LifxLAN()
    l = lan.lights[0]
    l1 = lan.get_device_by_name('master 1')
    l2 = lan.get_device_by_name('master 2')
    labels = [l.label for l in lan.lights]
    for lab in sorted(labels):
        print(lab)
    print(l1.color)

    duration = 4
    orig = l1.color
    l2.set_color(Color.from_hex(0xf4d92, l2.color.kelvin), duration=duration * 1000)
    import time
    time.sleep(duration)
    l2.set_color(orig, duration=duration * 1000)
    return
    print(len(lan.lights))
    print(l.color)
    print(l.power_level)
    print(lan.get_color_all_lights())


if __name__ == '__main__':
    __main()
