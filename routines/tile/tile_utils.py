from collections import defaultdict, Counter
from contextlib import suppress
from functools import lru_cache
from itertools import islice, cycle, groupby, product, starmap
from types import SimpleNamespace
from typing import List, NamedTuple, Tuple, Dict, Optional, Callable, Iterable, Set, Union, Any

from PIL import Image

from lifxlan import RGBk, Color, Colors, init_log, timer
from routines import colors_to_theme, ColorTheme

__author__ = 'acushner'

log = init_log(__name__)
default_shape = 8, 8
default_color = Colors.OFF
Shape = Tuple[int, int]


class RC(NamedTuple):
    """represent row/column coords"""
    r: int
    c: int

    def to(self, other):
        """range from self to other"""
        yield from (RC(r, c)
                    for r in range(self.r, other.r)
                    for c in range(self.c, other.c))

    def in_bounds(self, rc_ul, rc_lr) -> bool:
        """return True if self inside the bounds of [upper_left, lower_right)"""
        return not (self[0] < rc_ul[0] or self[1] < rc_ul[1]
                    or self[0] >= rc_lr[0] or self[1] >= rc_lr[1])

    @property
    def area(self):
        return self.r * self.c

    def __add__(self, other) -> 'RC':
        return RC(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other) -> 'RC':
        return RC(self[0] - other[0], self[1] - other[1])

    def __floordiv__(self, other) -> 'RC':
        return RC(self[0] // other[0], self[1] // other[1])

    def __mod__(self, other) -> 'RC':
        return RC(self[0] % other[0], self[1] % other[1])

    def __lt__(self, other):
        return self[0] < other[0] and self[1] < other[1]

    def __eq__(self, other):
        return self[0] == other[0] and self[1] == other[1]

    def __rmod__(self, other) -> 'RC':
        return self % other

    def __divmod__(self, other) -> Tuple['RC', 'RC']:
        return self // other, self % other

    def __neg__(self):
        return RC(-self[0], -self[1])


class TileInfo(NamedTuple):
    idx: int
    origin: RC


tile_map: Dict[RC, TileInfo] = {RC(1, 1): TileInfo(2, RC(0, 0)),
                                RC(1, 0): TileInfo(1, RC(0, 0)),
                                RC(0, 1): TileInfo(3, RC(0, 0)),
                                RC(2, -1): TileInfo(0, RC(1, 1)),
                                RC(0, 0): TileInfo(4, RC(1, 0))}


class DupesValids(NamedTuple):
    """
    used by ColorMatrix to help find bounding boxes for things
    """
    d: frozenset
    v: frozenset

    @property
    def first_valid(self):
        """return first valid value"""
        return min(self.v)

    @property
    def last_valid(self):
        """return last valid value"""
        return max(self.v)

    @property
    @lru_cache()
    def by_group(self):
        """return tuples of (start, end) for valid regions"""
        t = sorted(self.v)
        gb = groupby(zip(t, t[1:]), key=lambda p: (p[1] - p[0]) == 1)
        valids = (list(v) for k, v in gb if k)
        return [(v[0][0], v[-1][1]) for v in valids]


_sentinel = object()


class ColorMatrix(List[List[Color]]):
    """represent Colors in a 2d-array form that allows for easy setting of TileChain lights"""

    def __init__(self, lst: Iterable = _sentinel, *, wrap=False):
        if lst is _sentinel:
            super().__init__()
        else:
            super().__init__(lst)
        self.wrap = wrap

    def __getitem__(self, item):
        if self.wrap and isinstance(item, RC):
            item %= self.shape
        if isinstance(item, tuple):
            r, c = item
            return self[r][c]
        return super().__getitem__(item)

    def __setitem__(self, item, val):
        if isinstance(item, tuple):
            r, c = item
            self[r][c] = val
            return val
        return super().__setitem__(item, val)

    @classmethod
    def from_filename(cls, fn) -> 'ColorMatrix':
        """read a png in using pillow and convert to ColorMatrix"""
        im = Image.open(fn).convert('RGB')
        px = im.load()
        return ColorMatrix([RGBk(*px[c, r]).color
                            for c in range(im.width)]
                           for r in range(im.height))

    @classmethod
    def from_shape(cls, shape: Shape = default_shape, default: Color = default_color) -> 'ColorMatrix':
        """create a ColorMatrix with shape `shape` and colors set to `default`"""
        num_rows, num_cols = shape
        return cls([default for _ in range(num_cols)] for _ in range(num_rows))

    @classmethod
    def from_colors(cls, colors: List[Color], shape: Shape = (8, 8)):
        """convert a list of colors into a ColorMatrix of shape `shape`"""
        num_rows, num_cols = shape
        if len(colors) != num_rows * num_cols:
            raise ValueError('incompatible shape!')

        cm = cls.from_shape(shape)
        for r in range(num_rows):
            for c in range(num_cols):
                cm[r, c] = colors[r * num_rows + c]
        return cm

    @property
    def flattened(self) -> List[Color]:
        """flatten ColorMatrix to 1d-array (opposite of `from_colors`)"""
        return [c for row in self for c in row]

    @property
    def shape(self) -> Shape:
        """(num_rows, num_cols)"""
        return len(self), len(self[0])

    @property
    def height(self) -> int:
        return self.shape[0]

    @property
    def width(self) -> int:
        return self.shape[1]

    @property
    def by_coords(self) -> Tuple[RC, Color]:
        """yield coordinates and their colors"""
        yield from ((RC(r, c), color)
                    for r, row in enumerate(self)
                    for c, color in enumerate(row))

    def copy(self) -> 'ColorMatrix':
        return ColorMatrix([c for c in row] for row in self)

    def set_max_brightness_pct(self, brightness_pct):
        """set brightness in all colors to at most `brightness_pct` pct"""
        brightness = 65535 * min(100.0, max(0.0, brightness_pct)) // 100
        for rc, c in self.by_coords:
            self[rc] = c._replace(brightness=min(c.brightness, brightness))

    def strip(self, strip_color: Optional[Color] = None) -> 'ColorMatrix':
        """strip out empty rows/cols from sides of image"""
        row_info = self.duplicates(strip_color)
        col_info = self.T.duplicates(strip_color)

        res = ([color for c, color in enumerate(row)
                if col_info.first_valid <= c <= col_info.last_valid]
               for r, row in enumerate(self)
               if row_info.first_valid <= r <= row_info.last_valid)
        return ColorMatrix(res)

    def duplicates(self, sentinel_color: Optional[Color] = None) -> DupesValids:
        """
        return rows where all colors are either `sentinel_color` or dupes

        to get columns, simply call with `self.T.duplicates()`
        """
        dupes, valids = set(), set()

        for r, row in enumerate(self):
            it = iter(row)
            cur = sentinel_color or next(it)
            if any(color != cur for color in it):
                valids.add(r)
                continue
            dupes.add(r)

        return DupesValids(frozenset(dupes), frozenset(valids))

    def split(self, split_color: Optional[Color] = None) -> List['ColorMatrix']:
        """
        split image into boxes based on rows/columns of empty colors

         _________________
        | a | b | ccccccc |
        |-----------------|
        | d | e | fffffff |
        |-----------------|
        | g | h | iiiiiii |
        |___|___|_________|

        would end up with 9 images: a, b, ccccccc, d, e, fffffff, g, h, and iiiiiii 6 images

        """
        row_info = self.duplicates(split_color)
        col_info = self.T.duplicates(split_color)
        return [self.get_range(RC(r_start, c_start), RC(r_end + 1, c_end + 1), default_color)
                for r_start, r_end in row_info.by_group
                for c_start, c_end in col_info.by_group]

    def get_range(self, rc0, rc1, default: Color = default_color) -> 'ColorMatrix':
        """create new ColorMatrix from existing existing CM from the box bounded by rc0, rc1"""
        shape = rc1 - rc0
        cm = ColorMatrix.from_shape(shape)
        for rc in rc0.to(rc1):
            c = default
            with suppress(IndexError):
                c = self[rc]
            cm[rc - rc0] = c
        return cm

    def replace(self, color_map: Dict[Color, ColorTheme]):
        """
        modifies self
        replace colors from keys of color_map with colors from values in ColorMatrix
        """
        s = slice(0, 3)
        color_map = {k[s]: cycle(colors_to_theme(v)) for k, v in color_map.items()}

        for rc, c in self.by_coords:
            if c[s] in color_map:
                self[rc] = next(color_map[c[s]])

    def find_all(self, color: Union[Color, Set[Color]]):
        s = slice(0, 3)
        if isinstance(color, Color):
            color = {color}

        color = {c[s] for c in color}

        return [rc for rc, c in self.by_coords if c[s] in color]

    def to_tiles(self, shape=default_shape, offset: RC = RC(0, 0), bg: Color = Color(0, 0, 0)) \
            -> Dict[RC, 'ColorMatrix']:
        """
        return dict of RC -> ColorMatrix, where this RC represents
        the tile's coordinates vis-a-vis the rest of the group
         _______________
        |       |       |
        |(0, 0) | (0, 1)|
        |_______|_______|
        |       |       |
        |(1, 0) | (1, 1)|
        |_______|_______|
        """
        res = defaultdict(lambda: ColorMatrix.from_shape(shape, default=bg))
        for rc, color in self.by_coords:
            rc += offset
            tile, new_rc = divmod(rc, shape)
            res[tile][new_rc] = color
        return {tile_idx: cm.rotate_from_origin(tile_map.get(tile_idx, SimpleNamespace(origin=RC(0, 0))).origin)
                for tile_idx, cm in res.items()}

    def rotate_from_origin(self, origin: RC) -> 'ColorMatrix':
        n_r = {RC(0, 0): 0,
               RC(0, 1): 3,
               RC(1, 1): 2,
               RC(1, 0): 1}
        return self.rotate_clockwise(n_r[origin])

    def rotate_clockwise(self, n=1) -> 'ColorMatrix':
        m = self.copy()
        for _ in range(n):
            m.reverse()
            m = list(zip(*m))
        return self._from_zip(m)

    @property
    def T(self):
        """transpose"""
        return self._from_zip(zip(*self))

    @classmethod
    def _from_zip(cls, zipped_vals) -> 'ColorMatrix':
        """convert zipped transpositions back to list of lists and ultimately a ColorMatrix"""
        return cls([list(r) for r in zipped_vals])

    @property
    def color_str(self):
        res = [80 * '=', f'ColorMatrix: Shape{self.shape}']
        # encode groups with (color, num_repeats) tuples for less overhead
        groups = (((c, sum(1 for _ in v)) for c, v in groupby(row)) for row in self)
        res.extend(''.join(c.color_str('  ' * total, set_bg=True) for c, total in row) for row in groups)
        res.append(80 * '=')
        res.append('')
        return '\n'.join(res)

    @property
    def describe(self) -> str:
        """
        return a histogram string of sorts showing colors and a visual representation
        of how much of that color is present in the image
        """
        d = sorted(Counter(self.flattened).items(), key=lambda kv: -kv[1])
        return '\n'.join(f'{str(c):>68}: {c.color_str(" " * count, set_bg=True)}' for c, count in d)

    def cast(self, converter: Callable) -> 'ColorMatrix':
        """
        cast individual colors using the converter callable
        """
        return ColorMatrix([converter(c) for c in row] for row in self)

    def resize(self, shape: Shape = (8, 8)) -> 'ColorMatrix':
        """resize image using pillow and return a new ColorMatrix"""
        if self.shape == shape:
            return self.copy()

        cm = self.cast(lambda color: color.rgb[:3])

        im = Image.new('RGB', cm.shape, 'black')
        pixels = im.load()
        for c, r in product(range(im.width), range(im.height)):
            with suppress(IndexError):
                pixels[c, r] = cm[r][c]

        y, x = shape
        im = im.resize((x, y), Image.ANTIALIAS)
        pixels = im.load()
        res = ColorMatrix.from_shape(shape)

        for c, r in product(range(im.width), range(im.height)):
            with suppress(IndexError):
                res[r][c] = pixels[c, r]

        return res.cast(lambda rgb: Color.from_rgb(RGBk(*rgb)))


# utils

def to_n_colors(*colors, n=64):
    return list(islice(cycle(colors), n))


class ANode(NamedTuple):
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


if __name__ == '__main__':
    play()
