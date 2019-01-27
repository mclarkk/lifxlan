import random
import time
from concurrent.futures import wait
from concurrent.futures.thread import ThreadPoolExecutor
from copy import copy
from functools import partial
from itertools import cycle
from typing import Callable, Iterable

from lifxlan import Dir, GridLight, Group, Colors, grid, LifxLAN, init_log, exhaust
from routines import ColorTheme, init_grid, colors_to_theme, preserve_brightness
from routines.keyboard_utils import *

__author__ = 'acushner'

log = init_log(__name__)
dir_map = {up << 8: Dir.up, down << 8: Dir.down, left << 8: Dir.left, right << 8: Dir.right}


def _get_next_light(group: Group, gl: GridLight,
                    dirs: Iterable[Dir] = parse_keyboard_inputs(dir_map, separate_process=True)):
    for dir in dirs:
        cur_gl = gl
        found_light = False

        # this while loop allows for non-contiguous groups of lights to be traversed
        while not found_light:
            next_gl = cur_gl.move(dir)
            if next_gl == cur_gl:
                break

            if not group.get_device_by_name(next_gl.name):
                cur_gl = next_gl
                continue

            found_light = True
        else:
            gl = next_gl
            yield gl


def _delay(f: Callable, delay_secs: float):
    f()
    if delay_secs:
        time.sleep(delay_secs)


@preserve_brightness
def point_control(group: Group, point_color: ColorTheme, base_theme: Optional[ColorTheme] = None,
                  *, tail_delay_secs: float = 0, head_delay_secs: float = 0):
    """
    move a single point around a group of lights

    \b
    use tail_delay_secs to add a trail to your light movement

    \b
    use head_delay_secs to increase the transition time of your point

    \b
    point_color is a `ColorTheme` that determines what color the light will be as you move around your lights

    \b
    base_theme is a `ColorTheme` that sets the background of your lights over which the point moves
    """
    init_grid(group)
    threads = defaultdict(lambda: ThreadPoolExecutor(1))

    base_theme = colors_to_theme(base_theme) or None
    point_colors = cycle(colors_to_theme(point_color))

    with group.reset_to_orig():
        group.turn_on()
        if base_theme:
            group.set_theme(base_theme)
        orig_settings = {l.label: copy(l) for l in group}
        valid_light_names = list(set(grid) & {l.label for l in group})

        grid_light = grid[random.choice(valid_light_names)]
        lights = _get_next_light(group, grid_light)
        try:
            while True:
                p = threads[grid_light]

                set_f = partial(grid_light.light.set_color, next(point_colors), duration=(int(head_delay_secs * 1000)))
                p.submit(_delay, set_f, head_delay_secs)

                next_light = next(lights)

                reset_f = partial(grid_light.light.reset, orig_settings[grid_light.name], int(tail_delay_secs * 1000))
                p.submit(reset_f)

                grid_light = next_light

        except Exception as e:
            # wait for all threads to complete in background if necessary so that `reset_to_orig` will be called last
            exhaust(map(wait, threads.values()))

            if isinstance(e, KeyboardInterrupt):
                return
            raise


def __main():
    lifx = LifxLAN()
    point_control(lifx['living_room'] + lifx['buffet'] + lifx['floor'] + lifx['dining_room'] + lifx['kitchen'],
                  Colors.SNES_DARK_PURPLE, Colors.CYAN, tail_delay_secs=2)


if __name__ == '__main__':
    __main()
