import math
from itertools import cycle
from time import sleep, time
from typing import Optional, Union

import arrow

from lifxlan import LifxLAN, Group, Colors, Themes, Waveform, Color
from routines import ColorTheme, colors_to_theme


def breathe(lifx: Group, breath_time_secs=8, min_brightness_pct=30,
            max_brightness_pct=60,
            colors: Optional[ColorTheme] = None,
            duration_mins: Optional[Union[int, float]] = 20):
    """whatever lights you pass in will breathe"""
    theme = colors_to_theme(colors)
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
    """toggle power on lights every `blink_time_secs`"""
    num_cycles = math.ceil(how_long_secs / blink_time_secs)
    with lifx.reset_to_orig():
        lifx.turn_off()
        for _, power in zip(range(num_cycles), cycle(range(2))):
            lifx.set_power(power)
            sleep(blink_time_secs)


def blink_color(lifx: Group, colors: Optional[ColorTheme] = None, blink_time_secs=.5, how_long_secs=8):
    """change colors on lights every `blink_time_secs`"""
    num_cycles = math.ceil(how_long_secs / blink_time_secs)
    theme = colors_to_theme(colors) or (Colors.COPILOT_BLUE, Colors.COPILOT_DARK_BLUE)
    with lifx.reset_to_orig():
        for _, color in zip(range(num_cycles), cycle(theme)):
            lifx.set_color(color)
            sleep(blink_time_secs)


def rainbow(lifx: Group, colors: Optional[ColorTheme] = Themes.rainbow,
            duration_secs=0.5, smooth=False):
    """similar to blink_color"""
    theme = colors_to_theme(colors)
    transition_time_ms = duration_secs * 1000 if smooth else 0
    rapid = duration_secs < 1
    with lifx.reset_to_orig():
        for color in theme:
            lifx.set_color(color, transition_time_ms, rapid)
            sleep(duration_secs)


def cycle_themes(lifx: Group, *themes: ColorTheme,
                 rotate_secs: Optional[int] = 60,
                 duration_mins: Optional[int] = 20,
                 transition_secs=5,
                 all_lights=True):
    """
    set lights to theme every `rotate_secs`.

    will round robin `themes`.
    rotation still works on one theme as it will re-assign the theme each `rotate_secs`
    """
    end_time = arrow.utcnow().shift(minutes=duration_mins or 100000)

    themes = [colors_to_theme(t) for t in themes]
    with lifx.reset_to_orig():
        for t in cycle(themes):
            if arrow.utcnow() > end_time:
                return
            lifx.set_theme(t, power_on=all_lights, duration=transition_secs * 1000)
            if rotate_secs:
                sleep(rotate_secs)
            else:
                sleep(duration_mins * 60 or 10000)


# ======================================================================================================================
# testing
def _set_waveforms(lifx: Group, waveform: Waveform, start_color: Color, end_color: Color,
                   *, period_msec=4000, num_cycles=4, skew_ratio=.5, reduce_sleep_msecs=0):
    lifx.turn_on()
    lifx.set_color(start_color)
    lifx.set_waveform(waveform, end_color, period_msec, num_cycles, skew_ratio=skew_ratio)
    sleep((period_msec * num_cycles - reduce_sleep_msecs) / 1000)


def fireworks(lifx: Group):
    """make lights look like fireworks"""
    start_color = Colors.SNES_LIGHT_PURPLE
    with lifx.reset_to_orig():
        lifx.set_color(start_color)
        sleep(1)
        for pers in (500, 250, 125, 60, 30):
            num_cycles = 1000 // pers
            _set_waveforms(lifx, Waveform.pulse, start_color, Colors.SNES_DARK_PURPLE, period_msec=pers,
                           num_cycles=num_cycles, reduce_sleep_msecs=100)


def waveforms(lifx: Group, waveform: Waveform, start_color: Color, end_color: Color,
              *, period_msec=4000, num_cycles=4, skew_ratio=.5):
    """test out waveforms"""
    with lifx.reset_to_orig():
        _set_waveforms(lifx, waveform, start_color, end_color, period_msec=period_msec, num_cycles=num_cycles,
                       skew_ratio=skew_ratio)


# ======================================================================================================================

def __main():
    lifx = LifxLAN()
    # lifx = lifx['living_room'] + lifx['kitchen']
    # lifx.set_color(Colors.DEFAULT)
    # blink_color(lifx, blink_time_secs=3)
    # rainbow(lifx, duration_secs=4, smooth=True)
    # breathe(lifx, colors=(Colors.SNES_LIGHT_PURPLE, Colors.SNES_DARK_PURPLE), min_brightness_pct=20)
    # themes = Themes.xmas, Themes.snes, Themes.copilot
    # themes = [(Colors.SNES_DARK_PURPLE, Colors.SNES_LIGHT_PURPLE),
    #           (Colors.COPILOT_BLUE, Colors.COPILOT_DARK_BLUE),
    #           (Colors.RED, Colors.GREEN)]
    # lifx = lifx['creative_space']
    # cycle_themes(lifx, Themes.xmas, rotate_secs=60, duration_mins=60, transition_secs=60)
    # with lifx.reset_to_orig():
    #     lifx.turn_on()
    #     breathe(lifx, colors=Colors.YALE_BLUE, min_brightness_pct=20, max_brightness_pct=70)
    # fireworks(lifx)
    # waveforms(lifx, Waveform.pulse, Colors.SNES_DARK_PURPLE, Colors.PYTHON_LIGHT_BLUE, skew_ratio=.3)
    lifx = lifx['living_room'] + lifx['kitchen'] + lifx['dining_room']
    fireworks(lifx)
    # lifx.turn_on()
    # sleep(3)
    # lifx.turn_off()
    print(lifx.off_lights)


if __name__ == '__main__':
    __main()
