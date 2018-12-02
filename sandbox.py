import random
from itertools import groupby


from lifxlan import Color, exhaust, LifxLAN
from lifxlan.settings import Colors, Themes
import time

d = dict(a=3, b=3, c=1)


def get_vals(n):
    keys, vals = zip(*d.items())
    print(keys, vals)
    return random.choices(keys, vals, k=n)


def __main():
    print(Colors)
    c = Colors.YALE_BLUE
    print(c.offset_hue(60))
    exhaust(map(print, Themes.snes))
    # exhaust(map(print, c.get_complements(1)))
    # exhaust(map(print, c.get_complements(1)))
    comps = c.get_complements(.2)
    # print(len(comps))
    lan = LifxLAN()
    print(lan.lights)
    return
    m = lan.auto_group()['master']
    print(m)
    print(lan.on_lights)
    print(lan.off_lights)
    return
    exhaust(map(print, m.color_power.items()))
    return
    m.set_color(Colors.DEFAULT)
    return
    for c in Themes.snes:
        m.set_color(c)
        time.sleep(5)
    return
    c = Color.mean(*(c for _, c in Colors))
    print(c)
    m.set_color(c)
    time.sleep(4)
    m.set_color(Colors.DEFAULT)

    return

    # for _ in range(20):
    #     t = get_vals(1300)
    #     t.sort()
    #     gb = groupby(t)
    #     for k, v in gb:
    #         print(k, sum(1 for _ in v))
    #     print()
    #
    # return
    for _ in range(20):
        t = Themes.xmas.get_colors(27)
        t.sort()
        gb = groupby(t)
        for k, v in gb:
            print(k, sum(1 for _ in v))
        print()
    return
    lan = LifxLAN()
    print(lan.auto_group())
    print(lan.color_lights)
    return
    l1 = lan.get_device_by_name('test')
    # l2 = lan.get_device_by_name('master 2')
    labels = [l.label for l in lan.lights]
    for lab in sorted(labels):
        print(lab)
    print(l1.color)

    duration = 4
    orig = l1.color
    l2.set_color(Color.from_hex(0xf4d92, l2.color.kelvin), duration=duration * 1000)
    time.sleep(duration)
    l2.set_color(orig, duration=duration * 1000)
    return
    print(len(lan.lights))
    print(l.color)
    print(l.power_level)
    print(lan.get_color_all_lights())


if __name__ == '__main__':
    __main()
