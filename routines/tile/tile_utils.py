import logging

from collections import defaultdict
from contextlib import suppress
from functools import lru_cache
from itertools import islice, cycle, groupby
from math import ceil
from time import sleep
from typing import List, NamedTuple, Tuple, Dict

from PIL import Image

from lifxlan import RGBk, Color, LifxLAN, TileChain, Colors, Themes
from routines import colors_to_theme

__author__ = 'acushner'

log = logging.getLogger(__name__)

default_shape = 8, 8
default_color = Colors.OFF


class RC(NamedTuple):
    r: int
    c: int

    def to(self, other):
        """range from self `to` other"""
        for r in range(self.r, other.r):
            for c in range(self.c, other.c):
                yield RC(r, c)

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


class ColorMatrix(List[List[Color]]):
    def __getitem__(self, item):
        if isinstance(item, tuple):
            return self[item[0]][item[1]]
        return super().__getitem__(item)

    def __setitem__(self, item, val):
        if isinstance(item, tuple):
            self[item[0]][item[1]] = val
            return val
        return super().__setitem__(item, val)

    @classmethod
    def from_filename(cls, fn) -> 'ColorMatrix':
        im = Image.open(fn).convert('RGB')
        px = im.load()
        return ColorMatrix([RGBk(*px[c, r]).color
                            for c in range(im.width)]
                           for r in range(im.height))

    @classmethod
    def from_shape(cls, shape: Tuple[int, int] = default_shape, default: Color = default_color):
        """create a ColorMatrix with `shape` set to `default`"""
        num_rows, num_cols = shape
        return cls([default for _ in range(num_cols)] for _ in range(num_rows))

    @classmethod
    def as_shape(cls, shape: Tuple[int, int] = default_shape, *, colors):
        """take list of colors and force to shape"""
        num_rows, num_cols = shape
        if len(colors) != num_rows * num_cols:
            raise ValueError('incompatible shape!')

        cm = cls.from_shape(shape)
        for r in range(num_rows):
            for c in range(num_cols):
                cm[r, c] = colors[r * num_rows + c]
        return cm

    @property
    def shape(self):
        """(num_rows, num_cols)"""
        return len(self), len(self[0])

    @property
    def flattened(self):
        return [c for row in self for c in row]

    @property
    def height(self):
        return self.shape[0]

    @property
    def width(self):
        return self.shape[1]

    def by_coords(self) -> Tuple[RC, Color]:
        for r, row in enumerate(self):
            for c, color in enumerate(row):
                yield RC(r, c), color

    def set_max_brightness_pct(self, brightness_pct):
        brightness = 65535 * min(100.0, max(0.0, brightness_pct)) // 100
        for rc, c in self.by_coords():
            self[rc] = c._replace(brightness=min(c.brightness, brightness))

    def strip(self, strip_color: Color = default_color) -> 'ColorMatrix':
        """strip out empty_cols from sides of image"""
        strip_color = strip_color[:3]
        row_on, col_on = set(), set()
        for rc, color in self.by_coords():
            if color[:3] != strip_color:
                row_on.add(rc.r)
                col_on.add(rc.c)

        rows = range(min(row_on), max(row_on) + 1)
        cols = range(min(col_on), max(col_on) + 1)
        return ColorMatrix([self[r, c] for c in cols] for r in rows)

    def split(self, split_color: Color = default_color) -> List['ColorMatrix']:
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
        split_color = split_color[:3]
        split_rows = self._find_1d_splits(self, split_color)
        split_cols = self._find_1d_splits(self.T, split_color)

        res = [self.get_range(RC(r0, c0), RC(r1, c1)).strip()
               for r0, r1 in zip(*(2 * [iter(split_rows)]))
               for c0, c1 in zip(*(2 * [iter(split_cols)]))]

        return res

    def get_range(self, rc0, rc1, default: Color = default_color) -> 'ColorMatrix':
        """get box in range of rc0, rc1"""
        shape = rc1 - rc0
        cm = ColorMatrix.from_shape(shape)
        for rc in rc0.to(rc1):
            c = default
            with suppress(IndexError):
                c = self[rc]
            cm[rc - rc0] = c
        return cm

    @staticmethod
    def _find_1d_splits(cm, split_color: Color) -> List[int]:
        """iterate over ColorMatrix and find where entire rows/columns are split_color"""
        # splits = [-1] + [n for n, row in enumerate(cm) if all(c[:3] == split_color for c in row)]
        splits = [-1] + [n for n, row in enumerate(cm) if len({c[:3] for c in row}) == 1]
        print(cm.shape, splits)
        if len(splits) == 1:
            return [0, cm.height]

        gb = groupby(zip(splits, splits[1:]), key=lambda t: t[1] - t[0])
        groups = [list(group)[-1] for _, group in gb][:-1]
        addl = [0] if groups[0][0] == -1 else []
        return addl + [g[1] for g in groups]

    def replace(self, color_map: Dict):
        """replace colors in ColorMatrix with values in color_map"""
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
            tile, rc = divmod(rc, shape)
            res[tile][rc] = color
        return res

    def rotate_from_origin(self, origin: RC):
        n_r = {RC(0, 0): 0,
               RC(0, 1): 3,
               RC(1, 1): 2,
               RC(1, 0): 1}
        return self.rotate_clockwise(n_r[origin])

    def rotate_clockwise(self, n=1):
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
        return cls([list(r) for r in zipped_vals])


def to_n_colors(*colors, n=64):
    return list(islice(cycle(colors), n))


@lru_cache()
def get_tile_chain() -> TileChain:
    lifx = LifxLAN()
    return lifx['tile 1'][0]


tile_map = {RC(0, 0): TileInfo(2, RC(0, 0)),
            RC(0, 1): TileInfo(1, RC(1, 0)),
            RC(1, 0): TileInfo(3, RC(1, 0)),
            RC(1, 1): TileInfo(4, RC(0, 1))}


def cm_test(c: Color) -> ColorMatrix:
    cm = ColorMatrix.from_shape(default_shape)
    cm[0, 0] = cm[0, 1] = cm[1, 0] = cm[1, 1] = c
    return cm


def id_tiles(tc: TileChain):
    """set tiles to different colors in the corner to ID tile"""
    colors = 'RED', 'ORANGE', 'YELLOW', 'GREEN', 'CYAN'
    for ti in tile_map.values():
        name = colors[ti.idx]
        print(ti.idx, name)
        cm = cm_test(Colors[name])
        tc.set_tile_colors(ti.idx, cm.rotate_from_origin(ti.origin).flattened)


def set_cm(cm: ColorMatrix, offset=RC(0, 0)):
    cm = cm.strip().get_range(RC(0, 0) + offset, RC(16, 16) + offset)
    print(cm.shape)
    cm.set_max_brightness_pct(60)
    tiles = cm.to_tiles(offset=RC(0, 1))
    # return id_tiles(tc)

    idx_colors_map = {}
    for rc, ti in tile_map.items():
        cm = tiles[rc].rotate_from_origin(ti.origin)
        print(cm)
        cm.replace({default_color: Color(1, 1, 100, 9000)})
        # cm.replace({Color(0, 0, 0): default_color})
        idx_colors_map[ti.idx] = cm.flattened

    tc = get_tile_chain()
    tc.set_tilechain_colors(idx_colors_map)


def to_mario():
    set_cm(ColorMatrix.from_filename('/tmp/ms.png').strip())


def to_mm():
    cm = ColorMatrix.from_filename('./mm_walk.png')
    for i, cm in enumerate(cm.split()):
        print('====  ', i, cm.shape)
        c_offset = max(0, ceil(cm.width / 2 - 8))
        set_cm(cm, offset=RC(0, c_offset))
        sleep(5)


def to_link():
    cm = ColorMatrix.from_filename('./link.png')
    set_cm(cm)


def to_link_big():
    cm = ColorMatrix.from_filename('./link_all.png')
    splits = cm.split()
    print(len(splits))
    for i, cm in enumerate(cycle(splits)):
        print('====  ', i, cm.shape)
        # c_offset = max(0, ceil(cm.width / 2 - 8))
        set_cm(cm)
        sleep(1)

def red_octorock():
    cm = ColorMatrix.from_filename('./zelda_red_octorock.png')
    splits = cm.split()
    print(len(splits))
    for i, cm in enumerate(cycle(splits)):
        print('====  ', i, cm.shape)
        # c_offset = max(0, ceil(cm.width / 2 - 8))
        set_cm(cm)
        sleep(1)

def split_test():
    cm = ColorMatrix.from_filename('/tmp/m_small.png')
    cm.split()


def __main():
    # print(RC(8, 8) - RC(4, 5))
    # return split_test()
    tc = get_tile_chain()
    tc.set_tile_colors(0, to_n_colors(Colors.OFF))
    return red_octorock()
    return to_link_big()
    return to_link()
    return to_mm()
    return to_mario()
    tc = get_tile_chain()
    for i, c in enumerate((Color.from_hex(0), Colors.OFF)):
        tc.set_tile_colors(i, to_n_colors(c))
    tc.set_tile_colors(2, to_n_colors(Colors.STEELERS_BLACK, Color(1, 1, 1, 0)))
    tc.set_tile_colors(3, to_n_colors(Colors.STEELERS_BLACK, Colors.OFF, Colors.YALE_BLUE))
    # return my_test()


if __name__ == '__main__':
    __main()
