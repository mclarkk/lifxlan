from contextlib import suppress
from itertools import chain
from typing import Optional, NamedTuple

from lifxlan3 import init_log, Group, Themes, LifxLAN
from lifxlan3.routines import ColorTheme, colors_to_theme, parse_keyboard_inputs, left, right, up, down, ctrl_r, ctrl_w

__author__ = 'acushner'

log = init_log(__name__)

mults = dict(hue=65535 / 360,  # base mult: 1 degree
             brightness=65535 / 40,
             saturation=65535 / 40)


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
    keys = 'aoeu' if dvorak else 'asdf'
    for k, v in zip(keys, _equal_offset(2)):
        res[ord(k)] = AttrOffset('hue', v)
    for k, v in zip(keys.upper().replace(';', ':'), _equal_offset(2, 10)):
        res[ord(k)] = AttrOffset('hue', v)

    # saturation
    res[left << 8] = AttrOffset('saturation', -1)
    res[right << 8] = AttrOffset('saturation', 1)
    res[left << 16] = AttrOffset('saturation', 0, False)
    res[right << 16] = AttrOffset('saturation', 65535, False)

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

    # write light settings to screen
    res[ctrl_w] = AttrOffset('print', None)

    return res


def _get_offset() -> AttrOffset:
    keys = _init_keys()
    yield from parse_keyboard_inputs(keys)


def light_eq(lifx: Group, color_theme: Optional[ColorTheme] = None):
    """
    a light equalizer to play with HSBk

    \b
    - homerow controls hue
    - shift-homerow controls hue even more!

    \b
    - left/right controls saturation
    - shift-left/right mins/maxes saturation

    \b
    - down/up controls brightness
    - shift-down/up mins/maxes brightness

    - jk (dvorak)/cv (qwerty) control kelvin

    - ctrl-r resets

    - ctrl-w prints info to screen
    """

    def _init_lights():
        lifx.turn_on()
        if theme:
            lifx.set_theme(theme)

    theme = colors_to_theme(color_theme)

    with suppress(KeyboardInterrupt), lifx.reset_to_orig():
        _init_lights()

        for ao in _get_offset():
            if ao.attr == 'reset':
                _init_lights()

            elif ao.attr == 'print':
                for l in lifx:
                    print(l, l.color)

            else:
                getattr(lifx, f'set_{ao.attr}')(ao.value, offset=ao.as_offset)


def __main():
    # return getch_test()
    lifx = LifxLAN()
    # lifx.set_color(Colors.DEFAULT)
    print(lifx.on_lights)
    lifx = lifx['kitchen'] + lifx['living_room']
    # lifx = lifx['master']
    # lifx = lifx['living room 1']
    # control(lifx, [Colors.SNES_DARK_PURPLE, Colors.SNES_LIGHT_PURPLE])
    light_eq(lifx, Themes.copilot)
    # control(lifx, [Colors.DEFAULT])


if __name__ == '__main__':
    __main()
