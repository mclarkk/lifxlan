import random
from itertools import groupby

import lifxlan
from lifxlan import Color
from lifxlan.settings import Colors, Themes

d = dict(a=3, b=3, c=1)


def get_vals(n):
    keys, vals = zip(*d.items())
    print(keys, vals)
    return random.choices(keys, vals, k=n)


def __main():
    print(Colors)
    lan = lifxlan.LifxLAN()
    print(lan.lights)
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
    lan = lifxlan.LifxLAN()
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
