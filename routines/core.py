import math
from itertools import cycle
from time import sleep, time
from typing import Optional, Union

import arrow

from lifxlan import LifxLAN, Group, Colors, Themes
from routines import ColorTheme, colors_to_themes


def breathe(lifx: Group, breath_time_secs=8, min_brightness_pct=30,
            max_brightness_pct=60,
            colors: Optional[ColorTheme] = None,
            duration_mins: Optional[Union[int, float]] = 20):
    """whatever lights you pass in will breathe"""
    theme = colors_to_themes(colors)
    half_period_ms = breath_time_secs * 1000.0
    sleep_time = breath_time_secs
    duration_secs = duration_mins * 60 or float('inf')

    min_brightness = min_brightness_pct / 100.0 * 65535
    max_brightness = max_brightness_pct / 100.0 * 65535

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
        for i, power in zip(range(num_cycles), cycle(range(2))):
            lifx.set_power(power)
            sleep(blink_time_secs)


def blink_color(lifx: Group, colors: Optional[ColorTheme] = None, blink_time_secs=.5, how_long_secs=8):
    num_cycles = math.ceil(how_long_secs / blink_time_secs)
    theme = colors_to_themes(colors) or (Colors.COPILOT_BLUE, Colors.COPILOT_DARK_BLUE)
    with lifx.reset_to_orig():
        for i, color in zip(range(num_cycles), cycle(theme)):
            lifx.set_color(color)
            sleep(blink_time_secs)


def rainbow(lifx: Group, colors: Optional[ColorTheme] = Colors.RAINBOW,
            duration_secs=0.5, smooth=False):
    theme = colors_to_themes(colors)
    transition_time_ms = duration_secs * 1000 if smooth else 0
    rapid = duration_secs < 1
    with lifx.reset_to_orig():
        for color in theme:
            lifx.set_color(color, transition_time_ms, rapid)
            sleep(duration_secs)


def set_theme(lifx: Group, *themes: ColorTheme,
              rotate_secs: Optional[int] = 60,
              duration_mins: Optional[int] = 20,
              transition_secs=5,
              all_lights=True):
    """
    set lights to theme every rotate seconds.

    will round robin `themes`.
    rotation still works on one theme as it will re-assign the theme each rotate_seconds
    """
    end_time = arrow.utcnow().shift(minutes=duration_mins or 100000)

    themes = [colors_to_themes(t) for t in themes]
    with lifx.reset_to_orig():
        for t in cycle(themes):
            if arrow.utcnow() > end_time:
                return
            lifx.set_theme(t, power_on=all_lights, duration=transition_secs * 1000)
            if rotate_secs:
                sleep(rotate_secs)
            else:
                sleep(duration_mins * 60 or 10000)


def __main():
    lifx = LifxLAN()
    lifx = lifx['living_room'] + lifx['kitchen']
    # lifx.set_color(Colors.DEFAULT)
    # blink_color(lifx, blink_time_secs=3)
    # rainbow(lifx, duration_secs=4, smooth=True)
    # breathe(lifx, colors=(Colors.SNES_LIGHT_PURPLE, Colors.SNES_DARK_PURPLE), min_brightness_pct=20)
    # themes = Themes.xmas, Themes.snes, Themes.copilot
    # themes = [(Colors.SNES_DARK_PURPLE, Colors.SNES_LIGHT_PURPLE),
    #           (Colors.COPILOT_BLUE, Colors.COPILOT_DARK_BLUE),
    #           (Colors.RED, Colors.GREEN)]
    # lifx = lifx['creative_space']
    set_theme(lifx, Themes.xmas, rotate_secs=60, duration_mins=60, transition_secs=60)
    print(lifx.on_lights)


if __name__ == '__main__':
    __main()
