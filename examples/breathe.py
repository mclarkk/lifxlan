#!/usr/bin/env python
# coding=utf-8
from time import sleep, time

from lifxlan import LifxLAN, Colors, Theme


def main():
    # instantiate LifxLAN client, it's wide to set TOTAL_NUM_LIGHTS in settings, but not necessary
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.
    half_period_ms = 8000
    sleep_time = half_period_ms / 1000
    duration_mins = 20
    duration_secs = duration_mins * 60
    min_brightness = .4 * 65536

    lifx = LifxLAN()
    lifx = lifx.auto_group()['master']

    with lifx.reset_to_orig(half_period_ms):
        lifx.set_brightness(.6 * 65536)
        lifx.set_theme(Theme.from_colors(Colors.SNES_LIGHT_PURPLE, Colors.SNES_DARK_PURPLE))
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


if __name__ == "__main__":
    main()
