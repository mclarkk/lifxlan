from enum import Enum
from typing import Dict

from .group import Group
from .light import Light

__author__ = 'acushner'

grid: Dict[str, 'GridLight'] = {}


def enlighten_grid(group: Group):
    """set lifxlan.Light objects on each GridLight based on `group`"""
    for light in group:
        if light.label in grid:
            grid[light.label].light = light
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
    def __init__(self, name):
        self.name = name
        self.neighbors: Dict[Dir, GridLight] = {}
        self.light: Light = None  # to be set later
        grid[name] = self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __setitem__(self, direction: Dir, light: 'GridLight', one_way: bool = False):
        self.neighbors[direction] = light
        if not one_way:
            light.neighbors[-direction] = self

    def move(self, direction: Dir):
        return self.neighbors.get(direction, self)

    def __str__(self):
        return f'{type(self).__name__}: {self.name!r}'

    __repr__ = __str__
