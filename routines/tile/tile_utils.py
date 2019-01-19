from collections import defaultdict
from contextlib import suppress
from functools import lru_cache
from itertools import islice, cycle, groupby
from math import ceil
from time import sleep
from typing import List, NamedTuple, Tuple, Dict, Optional

from PIL import Image

from lifxlan import RGBk, Color, LifxLAN, TileChain, Colors, init_log
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

    def __add__(self, other) -> 'RC':
        return RC(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other) -> 'RC':
        return RC(self[0] - other[0], self[1] - other[1])

    def __floordiv__(self, other) -> 'RC':
        return RC(self[0] // other[0], self[1] // other[1])

    def __mod__(self, other) -> 'RC':
        return RC(self[0] % other[0], self[1] % other[1])

    def __divmod__(self, other) -> Tuple['RC', 'RC']:
        return self // other, self % other


class TileInfo(NamedTuple):
    idx: int
    origin: RC


class DupesValids(NamedTuple):
    d: frozenset
    v: frozenset

    @property
    @lru_cache()
    def first_valid(self):
        """return first valid value"""
        return min(self.v)

    @property
    @lru_cache()
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


tile_map: Dict[RC, TileInfo] = {RC(0, 0): TileInfo(2, RC(0, 0)),
                                RC(0, 1): TileInfo(1, RC(1, 0)),
                                RC(1, 0): TileInfo(3, RC(1, 0)),
                                RC(1, 1): TileInfo(4, RC(0, 1))}


class ColorMatrix(List[List[Color]]):
    """represent Colors in a 2d-array (roughly) form that allows for easy setting of Tilechain Lights"""

    def __getitem__(self, item):
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
        """create a ColorMatrix with `shape` set to `default`"""
        num_rows, num_cols = shape
        return cls([default for _ in range(num_cols)] for _ in range(num_rows))

    @classmethod
    def to_shape(cls, shape: Shape = default_shape, *, colors):
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
        """flatten ColorMatrix to 1d-array (opposite of `to_shape`)"""
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

    def by_coords(self) -> Tuple[RC, Color]:
        """yield coordinates and their colors"""
        yield from ((RC(r, c), color)
                    for r, row in enumerate(self)
                    for c, color in enumerate(row))

    def set_max_brightness_pct(self, brightness_pct):
        """set brightness in all colors to at most `brightness_pct` pct"""
        brightness = 65535 * min(100.0, max(0.0, brightness_pct)) // 100
        for rc, c in self.by_coords():
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
        return [self.get_range(RC(r_start, c_start), RC(r_end, c_end), default_color)
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
        """replace colors from keys of color_map with colors from values in ColorMatrix"""
        s = slice(0, 3)
        color_map = {k[s]: cycle(colors_to_theme(v)) for k, v in color_map.items()}

        for rc, c in self.by_coords():
            if c[s] in color_map:
                self[rc] = next(color_map[c[s]])

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
        for rc, color in self.by_coords():
            rc += offset
            tile, new_rc = divmod(rc, shape)
            res[tile][new_rc] = color
        return {tile_idx: cm.rotate_from_origin(tile_map[tile_idx].origin)
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


# utils

def to_n_colors(*colors, n=64):
    return list(islice(cycle(colors), n))


@lru_cache()
def get_tile_chain() -> TileChain:
    lifx = LifxLAN()
    return lifx.tilechain_lights[0]


def _cm_test(c: Color) -> ColorMatrix:
    cm = ColorMatrix.from_shape(default_shape)
    cm[0, 0] = cm[0, 1] = cm[1, 0] = cm[1, 1] = c
    return cm


def id_tiles(tc: TileChain, rotate=False):
    """set tiles to different colors in the corner to ID tile"""
    colors = 'MAGENTA', 'YELLOW', 'YALE_BLUE', 'GREEN', 'BROWN'
    for ti in tile_map.values():
        name = colors[ti.idx]
        print(ti.idx, name)
        cm = _cm_test(Colors[name])
        if rotate:
            cm = cm.rotate_from_origin(ti.origin)
        tc.set_tile_colors(ti.idx, cm.flattened)


# interactive

def animate(fn: str, *, center: bool = False, sleep_secs: float = .75):
    """split color matrix and change images every `sleep_secs` seconds"""
    cm = ColorMatrix.from_filename(fn)
    for i, cm in enumerate(cycle(cm.split())):
        log.info('.')
        c_offset = 0 if not center else max(0, ceil(cm.width / 2 - 8))
        set_cm(cm, offset=RC(0, c_offset))
        sleep(sleep_secs)


def set_cm(cm: ColorMatrix, offset=RC(0, 0)):
    cm = cm.strip().get_range(RC(0, 0) + offset, RC(16, 16) + offset)
    cm.set_max_brightness_pct(60)
    tiles = cm.to_tiles()

    idx_colors_map = {}
    for t_idx, cm in tiles.items():
        t_info = tile_map[t_idx]
        cm.replace({default_color: Color(1, 1, 100, 9000)})
        idx_colors_map[t_info.idx] = cm.flattened

    tc = get_tile_chain()
    tc.set_tilechain_colors(idx_colors_map)


def mario_one():
    set_cm(ColorMatrix.from_filename('./imgs/ms.png').strip())


def link_one():
    cm = ColorMatrix.from_filename('./imgs/link.png')
    set_cm(cm)


def mm():
    animate('./imgs/mm_walk.png', center=True)


def link():
    animate('./imgs/link_all.png')


def red_octorock():
    fn = './imgs/zelda_red_octorock.png'
    # return ColorMatrix.from_filename(fn).strip()
    animate(fn)


def ghosts():
    animate('./imgs/zelda_ghosts.png')


def split_test():
    cm = ColorMatrix.from_filename('/tmp/m_small.png')
    cm.split()


def __main():
    # print(RC(8, 8) - RC(4, 5))
    # return split_test()
    # tc = get_tile_chain()
    # tc.set_tile_colors(0, to_n_colors(Colors.OFF))
    # return animate('./imgs/zelda_enemies.png')
    # return ghosts()
    # return red_octorock()
    return link()
    return link_one()
    return mm()
    return mario_one()


if __name__ == '__main__':
    __main()
