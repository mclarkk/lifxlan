from enum import Enum
from typing import Dict

from .devices.light import Light

__author__ = 'acushner'

grid: Dict[str, 'GridLight'] = {}


def enlighten_grid(group):
    """ set lifxlan.Light objects on each GridLight based on `group`

    call from your grid_local.py file to set up how your home grid looks
    """
    from .group import Group
    group: Group
    for light in group:
        if light.label in grid:
            grid[light.label].light = light
    return grid


class Dir(Enum):
    """represent neighbor directions in light grid"""
    up = 'up'  # for my place, 'up' is west
    right = 'right'
    down = 'down'
    left = 'left'

    def __neg__(self):
        return dirs[(dirs[self] + 2) % len(dirs)]

    def __next__(self):
        return dirs[(dirs[self] + 1) % len(dirs)]


dirs = {d: idx for idx, d in enumerate(Dir)}


class GridLight:
    """represent a light in a grid including its neighbors"""

    def __init__(self, name):
        self.name = name
        self.neighbors: Dict[Dir, GridLight] = {}
        self.light: Light = None  # to be set later
        grid[name] = self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __setitem__(self, direction: Dir, neighbor: 'GridLight', one_way: bool = False):
        """add neighbor to light"""
        self.neighbors[direction] = neighbor
        if not one_way:
            neighbor.neighbors[-direction] = self

    def move(self, direction: Dir):
        return self.neighbors.get(direction, self)

    def __str__(self):
        return f'{type(self).__name__}: {self.name!r}'

    __repr__ = __str__
