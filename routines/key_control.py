"""
control lights using keyboard keys:

homerow controls hue
shift-homerow controls hue even more!

right/left controls saturation
shift-right/left maxes/mins saturation

up/down controls brightness
shift-up/down maxes/mins brightness

jk (dvorak)/cv (qwerty) control kelvin

ctrl-r resets
"""
from collections import defaultdict
from getch import getch
from itertools import chain
from typing import Optional, NamedTuple

import arrow

from lifxlan import init_log, Group, Themes, LifxLAN, Colors, exhaust
from routines import ColorTheme, colors_to_theme

__author__ = 'acushner'

log = init_log(__name__)

esc = 0x1b
l_bracket = 0x5b
dirs = up, down, right, left = 0x41, 0x42, 0x43, 0x44
one = 0x31
two = 0x32
semi = 0x3b
enter = 0xa
ctrl_r = 0x12

mults = dict(hue=65535 / 360,  # base mult: 1 degree
             brightness=65535 / 20,  # 10%
             saturation=65535 / 20)


class AttrOffset(NamedTuple):
    attr: str
    offset: int
    as_offset: bool = True

    @property
    def value(self):
        if self.as_offset:
            return self.offset * mults.get(self.attr, 1)
        return self.offset


def _init_keys(qwerty=False):
    """map key presses to AttrOffset objects that determine how lights are controlled"""
    dvorak = not qwerty

    def _equal_offset(n, mult=1):
        return [mult * v for v in chain(range(-n, 0), range(1, n + 1))]

    res = {}

    # hue
    keys = 'aoeuhtns' if dvorak else 'asdfjkl;'
    for k, v in zip(keys, _equal_offset(4)):
        res[ord(k)] = AttrOffset('hue', v)
    for k, v in zip(keys.upper().replace(';', ':'), _equal_offset(4, 10)):
        res[ord(k)] = AttrOffset('hue', v)

    # saturation
    res[left << 8] = AttrOffset('saturation', -1)
    res[right << 8] = AttrOffset('saturation', 1)
    res[left << 16] = AttrOffset('saturation', 65535, False)
    res[right << 16] = AttrOffset('saturation', 0, False)

    # brightness
    res[up << 8] = AttrOffset('brightness', 1)
    res[down << 8] = AttrOffset('brightness', -1)
    res[up << 16] = AttrOffset('brightness', 65535, False)
    res[down << 16] = AttrOffset('brightness', 0, False)

    # kelvin
    res[ord('k' if dvorak else 'v')] = AttrOffset('kelvin', 25)
    res[ord('j' if dvorak else 'c')] = AttrOffset('kelvin', -25)
    res[ord('K' if dvorak else 'V')] = AttrOffset('kelvin', 100)
    res[ord('J' if dvorak else 'C')] = AttrOffset('kelvin', -100)

    # reset
    res[ctrl_r] = AttrOffset('reset', None)

    return res


def _parse_chars():
    """
    handle multi-byte chars such as 'up', 'ctrl-r', and 'shift-left'

    this is confusing.

    simple ascii chars will appear as one byte, like 0x41 -> 'A'

    some inputs, however, are multiple bytes, together at once.
    consider pressing 'up', it appears as [0x1b, 0x5b, 0x41], which is in fact [ESC, '[', 'A']]
    the below handles that by using some sort of state machine as represented by `tree`
    """

    def _create_tree():
        return defaultdict(_create_tree)

    # this tree handles multi-byte chars
    tree = _create_tree()
    mod1 = tree[esc][l_bracket]
    shift = mod1[one][semi][two]

    node = tree
    state = 0
    while True:
        c = ord(getch())

        node = node.get(c)
        if node is mod1 or node is shift:
            state += 1
        if node is not None:
            continue

        yield c << (state * 8)

        node = tree
        state = 0


def _get_offset() -> AttrOffset:
    keys = _init_keys()
    for c in _parse_chars():
        if c in keys:
            yield keys[c]


def control(lifx: Group, color_theme: Optional[ColorTheme] = None):
    def _init_lights():
        lifx.turn_on()
        if theme:
            lifx.set_theme(theme)

    theme = colors_to_theme(color_theme)

    with lifx.reset_to_orig():
        _init_lights()

        for ao in _get_offset():
            if ao.attr == 'reset':
                _init_lights()
            else:
                getattr(lifx, f'set_{ao.attr}')(ao.value, offset=ao.as_offset)


def getch_test():
    """run with this to see what chars lead to what bytes"""

    def _getch_test():
        last_update = arrow.utcnow()
        while True:
            c = getch()
            if (arrow.utcnow() - last_update).total_seconds() > .05:
                print()
                last_update = arrow.utcnow()
            print('got', hex(ord(c)))

    exhaust(_getch_test())


def __main():
    # return getch_test()
    lifx = LifxLAN()
    # lifx.set_color(Colors.DEFAULT)
    print(lifx.on_lights)
    # lifx = lifx['kitchen'] + lifx['living_room']
    lifx = lifx['master']
    # lifx = lifx['living room 1']
    control(lifx, [Colors.SNES_DARK_PURPLE, Colors.SNES_LIGHT_PURPLE])
    # control(lifx, [Colors.DEFAULT])


if __name__ == '__main__':
    __main()
