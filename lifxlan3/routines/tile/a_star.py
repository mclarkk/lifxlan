
from contextlib import suppress
from itertools import product
from typing import Any, Iterable, List, NamedTuple, Optional, Set, Tuple

from lifxlan3.routines.tile.tile_utils import RC, ColorMatrix
from lifxlan3.utils import timer


class ANode(NamedTuple):
    """represent a node in A* algo"""
    parent: Optional['ANode']
    pos: RC
    g: int = 0  # distance to start node
    h: int = 0  # heuristic for distance to goal

    @property
    def f(self) -> float:
        return self.g + self.h

    @classmethod
    def create(cls, parent: 'ANode', pos, *goals: RC):
        g = cls.calc_g(parent)
        h = cls.calc_h(pos, *goals)
        return cls(parent, pos, g, h)

    @staticmethod
    def calc_g(parent: Optional['ANode']):
        return (parent.g if parent else 0) + 1

    @staticmethod
    def calc_h(pos: RC, *goals: RC):
        diffs = (g - pos for g in goals)
        return min(rc.r ** 2 + rc.c ** 2 for rc in diffs)

    def __eq__(self, other):
        return self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)


def _get_path(node: ANode) -> List[RC]:
    res = [node.pos]
    p = node.parent
    while p:
        res.append(p.pos)
        p = p.parent
    res.reverse()
    return res


def _create_children(shape_ul: RC, shape_lr: RC, impassable: Set[RC], n: ANode, goals: Iterable[RC]) -> List[ANode]:
    offsets = RC(1, 0), RC(0, 1), RC(-1, 0), RC(0, -1)
    res = []

    for o in offsets:
        rc = n.pos + o
        if rc in impassable:
            continue

        if not rc.in_bounds(shape_ul, shape_lr):
            continue

        res.append(ANode.create(n, rc, *goals))

    return res


class WrappedGoals(NamedTuple):
    bounds: Tuple[RC, RC]
    goals: Set[RC]
    impassable: Set[RC]


def _create_wrapped_goals(shape: RC, goal: RC, impassable: Set[RC]) -> WrappedGoals:
    """set up maze for when an object is allowed to wrap around the screen"""
    s = RC(*shape)
    r_offsets = -s.r, 0, s.r
    c_offsets = -s.c, 0, s.c
    offsets = [RC(*rc) for rc in product(r_offsets, c_offsets)]
    goals = {goal - rc for rc in offsets}
    impassables = {impass - rc for impass in impassable for rc in offsets}
    bounds = -shape, shape + shape

    return WrappedGoals(bounds, goals, impassables)


# TODO: write custom a_star that deals with moving snek
@timer
def a_star(maze: List[List[Any]], start: RC, end: RC, impassable: Set[RC] = frozenset(), allow_wrap=False):
    """return a* path for maze"""
    start_n = ANode(None, start)
    shape_ul, shape_lr = RC(0, 0), RC(len(maze), len(maze[0]))

    if allow_wrap:
        (shape_ul, shape_lr), goals, impassable = _create_wrapped_goals(shape_lr, end, impassable)
    else:
        goals = {end, }

    opened, closed = [start_n], set()

    while opened:
        cur_n, cur_i = opened[0], 0

        for i, n in enumerate(opened):
            if n.f < cur_n.f:
                cur_n, cur_i = n, i

        closed.add(opened.pop(cur_i))

        # found the end
        if cur_n.pos in goals:
            return _get_path(cur_n)

        children = _create_children(shape_ul, shape_lr, impassable, cur_n, goals)
        for c in children:
            if c in closed:
                continue

            with suppress(ValueError):
                opened_idx = opened.index(c)
                opened_c = opened[opened_idx]
                if c.g > opened_c.g:
                    continue
                opened.pop(opened_idx)

            opened.append(c)


def play():
    cm = ColorMatrix.from_shape((16, 16))
    start = RC(1, 1)
    end = RC(15, 15)
    impassable = {RC(r, c)
                  for r in range(2, 15)
                  for c in range(14)}
    print(a_star(cm, start, end, impassable, allow_wrap=True))