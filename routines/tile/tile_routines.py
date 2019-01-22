from functools import lru_cache
from math import ceil
from time import sleep

from lifxlan import TileChain, LifxLAN, Color, Colors, cycle, init_log
from routines.tile.tile_utils import ColorMatrix, default_shape, tile_map, RC, default_color

from pprint import pprint

__author__ = 'acushner'

log = init_log(__name__)


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
    _cmp_colors(idx_colors_map)


def _cmp_colors(idx_colors_map):
    from itertools import starmap
    tc = get_tile_chain()
    lights = {idx: list(starmap(Color, tc.get_tile_colors(idx).colors)) for idx in idx_colors_map}

    here_there = {k: set(idx_colors_map[k]) - set(lights[k])
                  for k in idx_colors_map}
    there_here = {k: set(lights[k]) - set(idx_colors_map[k])
                  for k in idx_colors_map}

    print('here - there')
    pprint(here_there)
    print()
    print('there - here')
    pprint(there_here)
    print()
    a = 4


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


def bernard_colors():
    cm = ColorMatrix.from_filename('./imgs/maniac_bernard.png')
    cm = cm


def __main():
    # print(RC(8, 8) - RC(4, 5))
    # return split_test()
    # tc = get_tile_chain()
    # tc.set_tile_colors(0, to_n_colors(Colors.OFF))
    # return bernard_colors()
    return animate('./imgs/maniac_bernard.png')
    # return ghosts()
    # return red_octorock()
    return link()
    return link_one()
    return mm()
    return mario_one()


if __name__ == '__main__':
    __main()
