from contextlib import suppress
from enum import Enum
from typing import Dict, Optional
from .group import Group
from .light import Light

__author__ = 'acushner'

grid: Dict[str, 'GridLight'] = {}


def enlighten_grid(lights: Group):
    for gl in grid.values():
        gl.light = lights.get_device_by_name(gl.name)
    return grid


class Dir(Enum):
    up = 'up'  # for my place, 'up' is west
    right = 'right'
    down = 'down'
    left = 'left'

    def __neg__(self):
        dirs = list(Dir)
        return dirs[(dirs.index(self) + 2) % len(dirs)]

    def __next__(self):
        dirs = list(Dir)
        return dirs[(dirs.index(self) + 1) % len(dirs)]


class GridLight:
    def __init__(self, name, light: Light = None):
        self.name = name
        self.neighbors: Dict[Dir, GridLight] = {}
        self.light = light  # to be set later
        grid[name] = self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def add(self, direction: Dir, light: 'GridLight'):
        self.neighbors[direction] = light
        light.neighbors[-direction] = self

    def __setitem__(self, direction: Dir, light: 'GridLight'):
        self.add(direction, light)

    def __str__(self):
        return f'{type(self).__name__}: {self.name!r}'

    def move(self, direction: Dir):
        for _ in range(4):
            with suppress(KeyError):
                return self.neighbors[direction]
            direction = next(direction)

        raise Exception('No neighbor found!')

    __repr__ = __str__


def __main():
    pass


if __name__ == '__main__':
    __main()
