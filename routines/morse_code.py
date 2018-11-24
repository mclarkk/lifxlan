"""
have your lights transmit messages in morse code.
"""
import logging
import sys
import time
from enum import Enum
from itertools import repeat
from typing import Union, List, TypeVar, Optional

from lifxlan import Group, Light, ThreadPoolExecutor, LifxLAN
from lifxlan.light import YALE_BLUE, RED, PURPLE, GOLD
from lifxlan.settings import ColorPower, PowerSettings, Color
from lifxlan.utils import WaitPool

__author__ = 'acushner'

log = logging.getLogger(__name__)

mc_char_len = {'.': 1, '-': 3, ' ': 1}
MORSE_CODE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                   'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                   'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
                   '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'}

TIME_QUANTUM_MS = 240


class OnOff(Enum):
    on = '\rX'
    off = '\r '


class Morse(List[str]):
    @classmethod
    def from_str(cls, s: str) -> 'Morse':
        res = cls(MORSE_CODE_DICT.get(c.upper(), ' ') for c in s)
        res.orig = s
        return res

    @property
    def ms_time(self):
        return TIME_QUANTUM_MS * (1 + sum(mc_char_len.get(c) for c in self.with_spaces))

    @property
    def with_spaces(self) -> str:
        return ' '.join(' '.join(self))

    def to_on_off(self):
        return [(OnOff.off if c == ' ' else OnOff.on, mc_char_len.get(c))
                for c in self.with_spaces]

    def simulate(self):
        print('simulating\n')
        for on_off, val in self.to_on_off():
            sys.stdout.write(on_off.value)
            time.sleep(val * TIME_QUANTUM_MS / 1000.)
        print('\ndone')


# m = Morse.from_str('sharifa')
# print(m)
# print(m.ms_time)
# print(m.with_spaces)
# print(m.to_on_off())
# print()
# m.simulate()

wp = WaitPool(ThreadPoolExecutor(8))


def morse_code(word_or_phrase: str, light: Union[Light, List[Light]],
               color_power_off: Optional[ColorPower] = ColorPower(None, 0),
               color_power_on: Optional[ColorPower] = None, *, reset=True):
    lights = [light] if isinstance(light, Light) else light
    m = Morse.from_str(word_or_phrase)
    orig = [ColorPower(l.color, l.power) for l in lights]
    d = {OnOff.on: color_power_on, OnOff.off: color_power_off}

    def get_color_iterable():
        if on_off is OnOff.on and not color_power_on:
            return orig
        return repeat(d[on_off])

    for on_off, val in m.to_on_off():
        print()
        print((on_off, val))
        with wp:
            wp.map(Light.set_color_power, lights, get_color_iterable())
            time.sleep(val * TIME_QUANTUM_MS / 1000.0)

    if reset:
        with wp:
            wp.map(Light.set_power, lights, repeat(0))
            time.sleep(3)
            wp.map(Light.set_color_power, lights, (ColorPower(c, p) for c, p in orig), repeat(3000))


on_color = ColorPower(RED, 1)
off_color = ColorPower(GOLD, 0)

if on_color:
    print('jeb')


def __main():
    lan = LifxLAN()
    print(lan.lights)
    l = lan.color_lights[0]
    l.set_color_power(ColorPower(PURPLE, 1))
    # l.set_power(0)
    morse_code('sharifa', l, color_power_on=on_color, color_power_off=off_color, reset=True)


if __name__ == '__main__':
    __main()
