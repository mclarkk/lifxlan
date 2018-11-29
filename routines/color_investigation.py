import logging
from getch import getch
import time
from itertools import repeat

from lifxlan import Colors, LifxLAN, Color

__author__ = 'acushner'

log = logging.getLogger(__name__)


def hex_vs_from_package_compare():
    c = Colors.YALE_BLUE
    c1, c2 = Colors.RED, Colors.YELLOW
    c1_hex, c2_hex = Color.from_hex(0xff0000), Color.from_hex(0xffff00)
    print(c1)
    print(c1_hex)
    print(c2)
    print(c2_hex)
    print('_____')
    print(c1 + c2)
    print(c1_hex + c2_hex)
    print(Colors.ORANGE)
    return (c1, c1_hex), (c2, c2_hex), (c1 + c2, c1_hex + c2_hex)


def low_vs_high_kelvin():
    colors = Colors.YALE_BLUE, Colors.RED, Colors.YELLOW
    return ((c._replace(kelvin=2500), c._replace(kelvin=9000)) for c in colors)


def offset_colors(degrees=30, n_iterations=10, c=Colors.YALE_BLUE):
    for _ in range(n_iterations):
        next_c = c.offset_hue(degrees)
        yield c, next_c
        c = next_c


def mean():
    print(Colors.YALE_BLUE + Colors.YALE_BLUE)
    c = Color.mean(Colors.YALE_BLUE, Colors.YALE_BLUE, Colors.YALE_BLUE)
    print(Colors.YALE_BLUE)
    print(c)


def hex_rgb_testing():
    val = 0xf4d92
    c = Color.from_hex(val)
    rgb = c.rgb
    print(rgb)
    print(hex(val))
    print(rgb.hex)

    t = rgb + rgb
    print((rgb + rgb).hex)
    print('____')
    print(c)
    print(c.rgb.color.rgb.color.rgb.color)

def __main():
    return mean()
    lan = LifxLAN()
    m = lan.auto_group()['master']
    l1, l2 = m
    # for cc1, cc2 in offset_colors(degrees=60):
    for cc1, cc2 in hex_vs_from_package_compare():
        print(cc1, cc2)
        print(l1.label, cc1.kelvin)
        l1.set_color(cc1)
        l2.set_color(cc2)
        time.sleep(2)
    m.set_color(Colors.DEFAULT)
    return

    print(Color.from_hex(0xff0000))
    m.set_color(Colors.DEFAULT)
    for l, _ in zip(repeat(m.lights), range(12)):
        l.set_color(c, duration=2000)
        c = c.offset_hue(30)
        time.sleep(2)

    m.set_color(Colors.DEFAULT, duration=2000)


if __name__ == '__main__':
    __main()
