"""
control lights using keyboard keys

homerow controls hue
shift-homerow controls hue even more!

up/down controls brightness
right/left controls saturation

shift-up/down maxes/mins brightness
shift-right/left maxes/mins saturation

ctrl-r resets
"""
from collections import defaultdict
from getch import getch
from itertools import chain
from typing import Optional, NamedTuple

import arrow

from lifxlan import init_log, Group, Themes, LifxLAN, Colors, exhaust
from routines import ColorTheme, colors_to_themes

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
             saturation=65535 / 20)  # 10%


class AttrOffset(NamedTuple):
    attr: str
    offset: int
    as_offset: bool = True

    @property
    def value(self):
        if self.as_offset:
            return self.offset * mults[self.attr]
        return self.offset


def _init_keys(qwerty=False):
    def _equal_offset(n, mult=1):
        return [mult * v for v in chain(range(-n, 0), range(1, n + 1))]

    res = {}

    keys = 'asdfjkl;' if qwerty else 'aoeuhtns'
    for k, v in zip(keys, _equal_offset(4)):
        res[ord(k)] = AttrOffset('hue', v)
    for k, v in zip(keys.upper().replace(';', ':'), _equal_offset(4, 10)):
        res[ord(k)] = AttrOffset('hue', v)

    ao_up = res[up << 8] = AttrOffset('brightness', 1)
    ao_down = res[down << 8] = AttrOffset('brightness', -1)

    if not qwerty:
        res[ord('k')] = ao_up
        res[ord('j')] = ao_down

    res[left << 8] = AttrOffset('saturation', -1)
    res[right << 8] = AttrOffset('saturation', 1)

    AO_UP = res[up << 16] = AttrOffset('brightness', 65535, False)
    AO_DOWN = res[down << 16] = AttrOffset('brightness', 0, False)

    if not qwerty:
        res[ord('K')] = AO_UP
        res[ord('J')] = AO_DOWN

    res[left << 16] = AttrOffset('saturation', 65535, False)
    res[right << 16] = AttrOffset('saturation', 0, False)

    res[ctrl_r] = AttrOffset('reset', None)

    return res


def _parse_chars():
    """handle multi-byte chars such as 'up', 'ctrl-r', and 'shift-left'"""

    def _create_tree():
        return defaultdict(_create_tree)

    # this tree handles multi-byte chars
    tree = _create_tree()
    mod1 = tree[esc][l_bracket]
    shift = mod1[one][semi][two]

    cur_d = tree
    state = 0
    while True:
        c = ord(getch())

        cur_d = cur_d.get(c)
        if cur_d is mod1 or cur_d is shift:
            state += 1
        if cur_d is not None:
            continue

        yield c << (state * 8)

        cur_d = tree
        state = 0


def _get_offset():
    keys = _init_keys()
    for c in _parse_chars():
        if c in keys:
            yield keys[c]


def control(lifx: Group, colors: Optional[ColorTheme] = None):
    theme = colors_to_themes(colors)

    def _init_lights():
        lifx.turn_on()
        if theme:
            lifx.set_theme(theme)

    with lifx.reset_to_orig() as settings:
        _init_lights()
        for ao in _get_offset():
            if ao.attr == 'reset':
                lifx.set_color_power(settings)
                _init_lights()
            else:
                getattr(lifx, f'set_{ao.attr}')(ao.value, offset=ao.as_offset)


def _getch_test():
    last_update = arrow.utcnow()
    while True:
        c = getch()
        if (arrow.utcnow() - last_update).total_seconds() > .05:
            print()
        print('got', hex(ord(c)), c)


def __main():
    # exhaust(_getch_test())
    # return
    lifx = LifxLAN()
    # lifx.set_color(Colors.DEFAULT)
    print(lifx.on_lights)
    lifx = lifx['kitchen'] + lifx['living_room']
    # lifx = lifx['living room 1']
    control(lifx, [Colors.SNES_DARK_PURPLE, Colors.SNES_LIGHT_PURPLE])


if __name__ == '__main__':
    __main()
