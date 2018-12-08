from itertools import count
from typing import Dict, Tuple

from .group import Group
from .light import Light
from .utils import init_log

__author__ = 'acushner'

log = init_log(__name__)

downstairs = [[None, 'buffet'],
              ['living room 4', 'living room 1', 'kitchen 4', 'kitchen 1', 'creative space 4', 'creative space 1'],
              ['living room 3', 'living room 2', 'kitchen 3', 'kitchen 1', 'creative space 3', 'creative space 2'],
              [None, 'floor']]

Lights = {'living room 1': (1, 0),
          'living room 2': (2, 0),
          'living room 3': (2, 0),
          'living room 4': (1, 0),
          'kitchen 1': (0, 0),
          'kitchen 2': (0, 0),
          'kitchen 3': (0, 0),
          'kitchen 4': (0, 0),
          'creative space 1': (0, 0),
          'creative space 2': (0, 0),
          'creative space 3': (0, 0),
          'creative space 4': (0, 0),
          }

Coord = Tuple[int, int]


class Grid:
    """represent lights in a grid formation"""

    def __init__(self, grid: Dict[Coord, Light], lights: Group):
        self._coord_light_grid = grid
        self._light_coord_grid: Dict[Light, Coord] = {v: k for k, v in grid.items()}
        self._lights = lights

    @classmethod
    def from_rows(cls, rows, lights: Group):
        res = {}
        label_light_map = {v: k for k, v in lights.label.items()}
        names = set(label_light_map)
        rows = [[name for name in r if name is None or name in names] for r in rows]
        r_count = count()
        for r in rows:
            if r:
                r_idx = next(r_count)
            c_count = count()
            for name in r:
                c_idx = next(c_count)
                if name is not None:
                    res[r_idx, c_idx] = label_light_map[name]
        return cls(res, lights)


def __main():
    pass


if __name__ == '__main__':
    __main()
