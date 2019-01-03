import random
from itertools import groupby
from typing import Iterable

from lifxlan import Color, exhaust, LifxLAN, Colors, Themes, Theme
import time

from lifxlan.grid import Grid, downstairs

d = dict(a=3, b=3, c=1)


def get_vals(n):
    keys, vals = zip(*d.items())
    print(keys, vals)
    return random.choices(keys, vals, k=n)


def grid_test():
    lights = LifxLAN().lights
    g = Grid.from_rows(downstairs, lights)


def test_powers():
    group = LifxLAN().color_lights
    with group.reset_to_orig(5000):
        group.set_power(0, 1000)
        time.sleep(1)

    for _ in range(5):
        group.refresh_power()
        print(group.power)
        time.sleep(.5)


def __main():
    # import routines
    # print(help(routines.core))
    # print(help(routines.morse_code))
    # print(help(routines.light_eq))
    lifx = LifxLAN()
    return
    print(Themes.xmas.color_str('xmas'))
    print((Themes.xmas + Theme.from_colors()).color_str('snth'))
    return
    print(Themes.xmas.get_colors(6))
    lifx = LifxLAN()
    # lifx.set_color(Colors.DEFAULT)
    with lifx.reset_to_orig():
        lifx.turn_on()
        lifx.set_theme(Themes.xmas)
        time.sleep(15)
    return
    return test_powers()
    return grid_test()
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
    ag = lan.auto_group()
    m = ag['master']
    print(m + ag['living_room'] + m)
    print(isinstance(m, Iterable))
    cs, vs = zip(*Colors)
    c = vs[0]
    print(len(c.get_complements(20)))
    print(c)
    c += vs[1]
    print(c, vs[0] + vs[1])
    print('JEB', Colors.sum(*vs))
    return

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
