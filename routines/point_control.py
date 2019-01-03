import random
from contextlib import suppress
from copy import copy
from itertools import cycle
from typing import Optional

from lifxlan import Dir, GridLight, Group, Colors, grid, LifxLAN
from routines import ColorTheme, init_grid, colors_to_theme
from routines.keyboard_utils import *

__author__ = 'acushner'

dir_map = {up << 8: Dir.up, down << 8: Dir.down, left << 8: Dir.left, right << 8: Dir.right}

parse_keyboard_inputs()


def _get_next_light(group: Group, gl: GridLight):
    for c in parse_keyboard_inputs():
        if c in dir_map:
            next_gl = gl.move(dir_map[c])
            if next_gl == gl or not group.get_device_by_name(next_gl.name):
                continue
            gl = next_gl
            yield gl


def point_control(group: Group, point_color: ColorTheme, base_theme: Optional[ColorTheme] = None,
                  *, tail_delay_secs: float = 0):
    """
    move a single point around a group of lights

    \b
    use tail_delay_secs to add a trail to your light movement

    \b
    point_color is a `ColorTheme` that determines what color the light will be as you move around your lights

    \b
    base_theme is a `ColorTheme` that sets the background of your lights over which the point moves
    """
    head_delay_secs = 0  # TODO: add implementation for this (need to delay resetting trailing lights)
    init_grid(group)
    base_theme = colors_to_theme(base_theme or Colors.DEFAULT)
    point_colors = cycle(colors_to_theme(point_color))
    tail_delay_secs += head_delay_secs

    with suppress(KeyboardInterrupt), group.reset_to_orig():
        group.turn_on()
        group.set_theme(base_theme)

        valid_light_names = list(set(grid) & {l.label for l in group})

        grid_light = grid[random.choice(valid_light_names)]
        next_lights = _get_next_light(group, grid_light)
        while True:
            orig_settings = copy(grid_light.light)
            grid_light.light.set_color(next(point_colors), duration=int(head_delay_secs * 1000))
            next_light = next(next_lights)
            grid_light.light.reset(orig_settings, int(tail_delay_secs * 1000))
            grid_light = next_light


def __main():
    lifx = LifxLAN()
    point_control(lifx['living_room'] + lifx['buffet'] + lifx['floor'] + lifx['dining_room'] + lifx['kitchen'],
                  Colors.SNES_DARK_PURPLE, Colors.CYAN, tail_delay_secs=2)


if __name__ == '__main__':
    __main()
