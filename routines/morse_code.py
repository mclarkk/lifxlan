"""
have your lights transmit messages in morse code.
"""
import logging
import time
from enum import Enum
from typing import Union, List, TypeVar

from lifxlan import Group, Light

__author__ = 'acushner'

log = logging.getLogger(__name__)

mc_char_len = {'.': 1, '-': 3, ' ': 1}
MORSE_CODE_DICT = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                   'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                   'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
                   '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'}

DOT_TIME_MS = 60


class OnOff(Enum):
    on = 'X'
    off = '\b \b'


class Morse(List[str]):
    @classmethod
    def from_str(cls, s: str) -> 'Morse':
        return cls(MORSE_CODE_DICT.get(c.upper()) for c in s)

    @property
    def ms_time(self):
        return DOT_TIME_MS * (1 + sum(mc_char_len.get(c) for c in self.with_spaces))

    @property
    def with_spaces(self) -> str:
        return ' '.join(' '.join(self))

    def to_on_off(self):
        return [(OnOff.off if c == ' ' else OnOff.on, mc_char_len.get(c))
                for c in self.with_spaces]

    def simulate(self):
        print('simulating')
        for on_off, val in self.to_on_off():
            print(on_off.value, end='', flush=True)
            time.sleep(DOT_TIME_MS / 100.)
        print('done')


m = Morse.from_str('sharifa')
print(m)
print(m.ms_time)
print(m.with_spaces)
print(m.to_on_off())
m.simulate()

print('j', end='')
print('j', end='')
print('j', end='')
print('j', end='')



def morse_code(word_or_phrase: str, light: Union[Light, List[Light]]):
    pass


def __main():
    pass


if __name__ == '__main__':
    __main()
