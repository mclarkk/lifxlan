"""
have your light/lights transmit messages in morse code.
"""
import sys
import time
from enum import Enum
from typing import Union, List, NamedTuple

from lifxlan3 import Group, Light, LifxLAN, exhaust, Colors, ColorPower, init_log
from lifxlan3.routines import preserve_brightness

__author__ = 'acushner'

log = init_log(__name__)

MORSE_CODE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                   'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                   'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
                   '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'}

TIME_QUANTUM_MS = 240


def mc_char_len(delay_time_ms=TIME_QUANTUM_MS):
    return {k: v * delay_time_ms / 1000 for k, v in (('.', 1), ('-', 3), (' ', 1))}


class OnOff(Enum):
    on = '\rX'
    off = '\r '


class Morse(List[str]):
    @classmethod
    def from_str(cls, s: str) -> 'Morse':
        res = cls(MORSE_CODE_DICT.get(c, ' ') for c in s.upper())
        res.orig = s
        return res

    @property
    def with_spaces(self) -> str:
        return ' '.join(' '.join(self)) + ' '

    def to_char_and_len(self, delay_time_ms=TIME_QUANTUM_MS):
        char_len = mc_char_len(delay_time_ms)
        return [(c, char_len[c]) for c in self.with_spaces]

    def simulate(self):
        print('simulating\n')
        char_len = mc_char_len()
        ons_offs = ((OnOff.off if c == ' ' else OnOff.on, char_len.get(c))
                    for c in self.with_spaces)
        for on_off, val in ons_offs:
            sys.stdout.write(on_off.value)
            time.sleep(val)
        print('\ndone')


class MCSettings(NamedTuple):
    dot: ColorPower = ColorPower(Colors.STEELERS_GOLD, 1)
    dash: ColorPower = dot
    space: ColorPower = ColorPower(None, 0)

    _char_idx_map = dict(zip('.- ', range(3)))

    def cp_from_char(self, char):
        return self[self._char_idx_map[char]]


@preserve_brightness
def morse_code(word_or_phrase: str,
               light_group: Union[Light, Group],
               delay_time_msec=TIME_QUANTUM_MS,
               settings: MCSettings = MCSettings()):
    """translate `word_or_phrase` into morse code that will appear on your lights"""
    light_group = Group([light_group]) if isinstance(light_group, Light) else light_group
    m = Morse.from_str(word_or_phrase)

    with light_group.reset_to_orig(3000):
        for c, length in m.to_char_and_len(delay_time_msec):
            light_group.set_color_power(settings.cp_from_char(c))
            time.sleep(length)


def __main():
    lan = LifxLAN()
    g = lan.auto_group()['master']
    exhaust(map(print, (light.power for light in g)))
    morse_code('s', g)


if __name__ == '__main__':
    __main()
