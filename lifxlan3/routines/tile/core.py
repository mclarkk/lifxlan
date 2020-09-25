import pkgutil
import time
from contextlib import suppress
from functools import lru_cache
from io import BytesIO
from itertools import count
from math import ceil
from pathlib import Path
from pprint import pprint
from random import choice, shuffle
from time import sleep
from typing import Optional, Dict, Union, Tuple

from PIL import Image

from lifxlan3 import TileChain, LifxLAN, Color, Colors, cycle, init_log, timer, Dir
from lifxlan3.routines.tile.tile_utils import ColorMatrix, default_shape, tile_map, RC, default_color

__author__ = 'acushner'

log = init_log(__name__)


@lru_cache()
def get_tile_chain() -> Optional[TileChain]:
    with suppress(IndexError):
        lifx = LifxLAN()
        return lifx.tilechain_lights[0]


def _cm_test(c: Color) -> ColorMatrix:
    cm = ColorMatrix.from_shape(default_shape)
    cm[0, 0] = cm[0, 1] = cm[1, 0] = cm[1, 1] = c
    return cm


def id_tiles(*, rotate=False):
    """set tiles to different colors in the corner to ID tile and help determine orientation"""
    tc = get_tile_chain()
    colors = 'MAGENTA', 'YELLOW', 'YALE_BLUE', 'GREEN', 'BROWN'
    for ti in tile_map.values():
        name = colors[ti.idx]
        print(ti.idx, name)
        cm = _cm_test(Colors[name])
        if rotate:
            cm = cm.rotate_from_origin(ti.origin)
        tc.set_tile_colors(ti.idx, cm.flattened)


_color_replacements: Dict[str, Dict[Color, Color]] = dict(
    crono={Color(hue=54612, saturation=65535, brightness=65535, kelvin=3200): Colors.OFF},
    ff4={Color(hue=32767, saturation=65535, brightness=65535, kelvin=3200): Colors.OFF},
    ff6={Color(hue=32767, saturation=65535, brightness=32896, kelvin=3200): Colors.OFF},
    smb2_items={Color(hue=21845, saturation=65535, brightness=65535, kelvin=3200): Color.from_hex(0x3ec7fb)},
    smk={Color(hue=21845, saturation=48059, brightness=65535, kelvin=3200): Colors.OFF,
         Color(hue=21845, saturation=52428, brightness=65535, kelvin=3200): Colors.OFF,
         Color(hue=21845, saturation=53115, brightness=63736, kelvin=3200): Colors.OFF,
         Color(hue=21250, saturation=51914, brightness=65535, kelvin=3200): Colors.OFF,
         Color(hue=21845, saturation=48427, brightness=63993, kelvin=3200): Colors.OFF},
    lttp={Color(hue=32767, saturation=65535, brightness=16448, kelvin=3200): Colors.OFF,
          Color(hue=32767, saturation=65535, brightness=32896, kelvin=3200): Colors.OFF},
    maniac={Color(hue=32767, saturation=65535, brightness=32896, kelvin=3200): Colors.OFF},
    zelda={Color(hue=35924, saturation=65535, brightness=32896, kelvin=3200): Colors.OFF},
)


def _get_color_replacements(filename):
    if isinstance(filename, BytesIO):
        return {}

    for k, v in _color_replacements.items():
        if k in filename:
            return v
    return {}


CFBI = Union[ColorMatrix, str, BytesIO, Image.Image]


def _init_cm(cm_or_fn_or_bytes_or_image: CFBI) -> Tuple[ColorMatrix, Dict[Color, Color]]:
    color_map = {}
    if isinstance(cm_or_fn_or_bytes_or_image, str):
        color_map = _get_color_replacements(cm_or_fn_or_bytes_or_image)
        cm_or_fn_or_bytes_or_image = Images.get_image(cm_or_fn_or_bytes_or_image)

    if isinstance(cm_or_fn_or_bytes_or_image, BytesIO):
        im = ColorMatrix.from_bytes(cm_or_fn_or_bytes_or_image)
    elif isinstance(cm_or_fn_or_bytes_or_image, Image.Image):
        im = ColorMatrix.from_image(cm_or_fn_or_bytes_or_image)
    elif isinstance(cm_or_fn_or_bytes_or_image, ColorMatrix):
        im = cm_or_fn_or_bytes_or_image
    else:
        raise TypeError(f'got {type(cm_or_fn_or_bytes_or_image)}, must be of type {CFBI}')

    return im, color_map


def animate(filename: CFBI,
            *, center: bool = False, sleep_secs: float = .75, in_terminal=False, size=RC(16, 16), strip=True,
            how_long_secs=30):
    """split color matrix and change images every `sleep_secs` seconds"""
    cm, color_map = _init_cm(filename)
    end_time = time.time() + how_long_secs
    splits = cm.split()
    shuffle(splits)
    for cm in cycle(splits):
        log.info('.')
        c_offset = 0 if not center else max(0, ceil(cm.width / 2 - 8))
        cm.replace(color_map)
        try:
            set_cm(cm, offset=RC(0, c_offset), size=size, in_terminal=in_terminal, strip=strip)
        except ValueError:
            continue
        sleep(max(0, min(sleep_secs, end_time - time.time())))
        if time.time() >= end_time:
            break


def translate(filename: CFBI, *, sleep_secs: float = .5, in_terminal=False,
              size=RC(16, 16), split=True, dir: Dir = Dir.right, n_iterations: int = None,
              strip=False, pixels_per_step=1):
    """move window over image

    `n_iterations` represents how many full iterations of the message itself"""
    cm, color_map = _init_cm(filename)
    if split:
        cm = cm.split()[0]

    mult = 1 if dir is Dir.right else -1

    def _gen_offset():
        its = count() if n_iterations is None else range(n_iterations)
        for _ in its:
            for _c_offset in range(0, cm.width - size.c, pixels_per_step):
                yield mult * (cm.width - _c_offset - 1)

    for c_offset in _gen_offset():
        cm.replace(color_map)
        cm.wrap = True
        set_cm(cm, offset=RC(0, c_offset), size=size, in_terminal=in_terminal, strip=strip)
        sleep(sleep_secs)


@timer
def set_cm(cm: ColorMatrix, offset=RC(0, 0), size=RC(16, 16),
           *, in_terminal=False, with_mini=True, strip=True, verbose=True,
           duration_msec=0):
    """set color matrix either in terminal or on lights"""
    if strip:
        cm = cm.strip()

    cm = cm.get_range(RC(0, 0) + offset, size + offset)

    if in_terminal:
        print(cm.color_str)
        if verbose:
            print(cm.describe)
            print(cm.resize().color_str)
            print(cm.resize((4, 4)).color_str)
        return

    cm.set_max_brightness_pct(60)
    tiles = cm.to_tiles()

    idx_colors_map = {}
    for t_idx, t_cm in tiles.items():
        t_info = tile_map[t_idx]
        t_cm.replace({default_color: Color(1, 1, 100, 9000)})
        idx_colors_map[t_info.idx] = t_cm.flattened

    if with_mini:
        ti = tile_map[RC(2, -1)]
        idx_colors_map[ti.idx] = cm.resize((8, 8)).rotate_from_origin(ti.origin).flattened

    tc = get_tile_chain()
    tc.set_tilechain_colors(idx_colors_map, duration=duration_msec)


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


# ======================================================================================================================
# IMAGES

class Images:
    images = None

    @classmethod
    def _init_images(cls):
        with suppress(FileNotFoundError):
            p = Path(__file__).parent.parent.parent / 'assets'
            cls.images = sorted(f.name for f in p.iterdir())

    @classmethod
    def get_random_image_name(cls, excluded=frozenset()):
        if cls.images:
            return choice(list(set(cls.images) - excluded))

    @staticmethod
    def get_image(name_or_bytes: Union[str, BytesIO]) -> BytesIO:
        if isinstance(name_or_bytes, BytesIO):
            return name_or_bytes
        return BytesIO(pkgutil.get_data('lifxlan3', f'assets/{name_or_bytes}'))


Images._init_images()


# ======================================================================================================================

def for_talk():
    return animate('text.png', sleep_secs=.5, strip=False)
    return id_tiles(rotate=False)
    return animate('m_small.png', sleep_secs=.75)
    return animate('ff4_tellah.png', sleep_secs=.75)


def __main():
    return for_talk()
    # return id_tiles(rotate=False)
    # return animate('./imgs/m_small.png', sleep_secs=.75)
    return animate('ff4_tellah.png', sleep_secs=.75)
    return translate('ff4_tellah.png', split=False, dir=Dir.left, sleep_secs=.1, n_iterations=4)
    return animate('mm_walk.png', sleep_secs=4, in_terminal=False)
    return animate('maniac_bernard.png')


if __name__ == '__main__':
    __main()
