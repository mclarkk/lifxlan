import math
from itertools import chain, repeat
from typing import Optional, List, Union, Iterable

from lifxlan import LifxLAN, Group, Colors, Color, Theme
from time import sleep, time

ColorTheme = Optional[Union[Color, Iterable[Color]]]


def _colors_to_themes(val: ColorTheme):
    if isinstance(val, Color):
        return Theme.from_colors(val)
    if isinstance(val, Theme):
        return val
    if isinstance(val, Iterable):
        return Theme.from_colors(*val)
    return val


def breathe(lifx: Group, breath_time_secs=8, min_brightness=.3 * 65536,
            max_brightness=.6 * 65536,
            colors: ColorTheme = None,
            duration_mins: Optional[Union[int, float]] = 20):
    """whatever lights you pass in will breathe"""
    theme = _colors_to_themes(colors)
    half_period_ms = breath_time_secs * 1000.0
    sleep_time = breath_time_secs
    duration_secs = duration_mins * 60 or float('inf')

    with lifx.reset_to_orig(half_period_ms):
        lifx.set_brightness(max_brightness, duration=10000)
        if theme:
            lifx.set_theme(theme)
        print("Breathing...")
        try:
            start_time = time()
            while True:
                with lifx.reset_to_orig(half_period_ms):
                    lifx.set_brightness(min_brightness, half_period_ms)
                    sleep(sleep_time)
                sleep(sleep_time)
                if time() - start_time > duration_secs:
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            print("Restoring original color and power to all lights...")


def blink_power(lifx: Group, blink_time_secs=.5, how_long_secs=8):
    num_cycles = math.ceil(how_long_secs / blink_time_secs)
    with lifx.reset_to_orig():
        lifx.turn_off()
        for i, power in zip(range(num_cycles), chain.from_iterable(repeat(range(2)))):
            lifx.set_power(power)
            sleep(blink_time_secs)


def blink_color(lifx: Group, colors: Optional[ColorTheme] = None, blink_time_secs=.5, how_long_secs=8):
    num_cycles = math.ceil(how_long_secs / blink_time_secs)
    theme = _colors_to_themes(colors) or (Colors.COPILOT_BLUE, Colors.COPILOT_DARK_BLUE)
    with lifx.reset_to_orig():
        for i, color in zip(range(num_cycles), chain.from_iterable(repeat(theme))):
            lifx.set_color(color)
            sleep(blink_time_secs)


def rainbow(lifx: Group, colors: Optional[ColorTheme] = Colors.RAINBOW,
            duration_secs=0.5, smooth=False):
    theme = _colors_to_themes(colors)
    transition_time_ms = duration_secs * 1000 if smooth else 0
    rapid = duration_secs < 1
    with lifx.reset_to_orig():
        for color in theme:
            lifx.set_color(color, transition_time_ms, rapid)
            sleep(duration_secs)


if __name__ == '__main__':
    lifx = LifxLAN()['master']
    lifx.set_color(Colors.DEFAULT)
    # blink_color(lifx, blink_time_secs=3)
    rainbow(lifx, duration_secs=4, smooth=True)
    # breathe(lifx, colors=(Colors.SNES_LIGHT_PURPLE, Colors.SNES_DARK_PURPLE))
