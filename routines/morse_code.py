"""
have your lights transmit messages in morse code.
"""
import logging
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


class Morse(List[str]):
    @classmethod
    def from_str(cls, s: str) -> 'Morse':
        return cls(MORSE_CODE_DICT.get(c.upper()) for c in s)

    @property
    def ms_time(self):
        s = ' '.join(' '.join(self))
        print(f'{s!r}')
        return DOT_TIME_MS * (1 + sum(mc_char_len.get(c) for c in s))


m = Morse.from_str('sharifa')
print(m)
print(m.ms_time)


def morse_code(light: Union[Light, List[Light]]):
    pass


def __main():
    pass


if __name__ == '__main__':
    __main()
