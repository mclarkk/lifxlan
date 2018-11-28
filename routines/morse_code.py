"""
have your light/lights transmit messages in morse code.
"""
import logging
import sys
import time
from enum import Enum
from typing import Union, List, NamedTuple

from lifxlan import Group, Light, LifxLAN, exhaust
from lifxlan.settings import ColorPower, Colors

__author__ = 'acushner'

log = logging.getLogger(__name__)

MORSE_CODE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                   'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                   'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
                   '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'}

TIME_QUANTUM_MS = 240
mc_char_len = {k: v * TIME_QUANTUM_MS / 1000 for k, v in {'.': 1, '-': 3, ' ': 1}.items()}


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
        return TIME_QUANTUM_MS + sum(mc_char_len[c] for c in self.with_spaces)

    @property
    def with_spaces(self) -> str:
        return ' '.join(' '.join(self)) + ' '

    def to_on_off(self):
        return [(OnOff.off if c == ' ' else OnOff.on, mc_char_len.get(c))
                for c in self.with_spaces]

    @property
    def to_char_and_len(self):
        return [(c, mc_char_len[c]) for c in self.with_spaces]

    def simulate(self):
        print('simulating\n')
        for on_off, val in self.to_on_off():
            sys.stdout.write(on_off.value)
            time.sleep(val * TIME_QUANTUM_MS / 1000.)
        print('\ndone')


class MCSettings(NamedTuple):
    dot: ColorPower = ColorPower(Colors.STEELERS_GOLD, 1)
    dash: ColorPower = dot
    space: ColorPower = ColorPower(None, 0)

    _char_idx_map = dict(zip('.- ', range(3)))

    def cp_from_char(self, char):
        return self[self._char_idx_map[char]]


def morse_code(word_or_phrase: str,
               light_group: Union[Light, Group],
               settings: MCSettings = MCSettings(),
               *, reset=True):
    light_group = Group([light_group]) if isinstance(light_group, Light) else light_group
    m = Morse.from_str(word_or_phrase)
    orig = {l: ColorPower(l.color, l.power) for l in light_group}
    print(orig)

    for c, length in m.to_char_and_len:
        light_group.set_color_power(settings.cp_from_char(c))
        time.sleep(length)

    if reset:
        light_group.set_power(0)
        time.sleep(1)
        light_group.set_color_power(orig, duration=3000)


def __main():
    lan = LifxLAN()
    # print(lan.lights)
    l = lan.auto_group()['master'].lights
    l.set_color(Colors.DEFAULT)
    exhaust(map(print, (light.power for light in l)))
    morse_code('sharifa', l.lights, reset=True)
    l = l


if __name__ == '__main__':
    __main()
