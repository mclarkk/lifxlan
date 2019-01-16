import operator as op
import random
from functools import reduce
from typing import List, Tuple, Optional

import click
from click import echo

import routines
from lifxlan import LifxLAN, Group, Colors, Color, Themes, Theme, ColorPower
from routines.keyboard_utils import getch_test as _getch_test
from routines import ColorTheme

__author__ = 'acushner'


class LifxProxy(LifxLAN):
    """proxy to LifxLAN. will only be created once when necessary"""

    def __init__(self):
        self._lights: LifxLAN = None

    def __getattribute__(self, item):
        lights = super().__getattribute__('_lights')
        if lights is None:
            lights = self._lights = LifxLAN()
        return getattr(lights, item)


lifx = LifxProxy()

DEFAULT_GROUP = 'ALL'


class Config:
    """main command config object"""

    def __init__(self):
        self.group: Group = None

        # properties
        self.brightness_pct: float = 100.0
        self.colors: List[Color] = []
        self.themes: List[Theme] = []

    @property
    def brightness_pct(self):
        return self._brightness_pct

    @brightness_pct.setter
    def brightness_pct(self, val):
        self._brightness_pct = min(100., max(0., val))

    @property
    def colors(self):
        return self._colors

    @colors.setter
    def colors(self, val: List[Color]):
        self._colors = [self.adjust_color(c) for c in val]

    @property
    def themes(self):
        return self._themes

    @themes.setter
    def themes(self, val: List[Theme]):
        self._themes = [self.adjust_theme(t) for t in val]

    def adjust_color(self, c: Color) -> Optional[Color]:
        if not c:
            return None
        return c._replace(brightness=int(c.brightness * (self.brightness_pct / 100)))

    def adjust_theme(self, t: Theme):
        """adjust theme for brightness_pct"""
        if not t:
            return None
        return Theme({self.adjust_color(c): w for c, w in t.items()})

    @property
    def color_theme(self) -> Optional[Theme]:
        try:
            self.validate_colors()
        except ValueError:
            return None

        color_theme = Theme.from_colors(*self.colors)
        themes = self.themes or []
        return reduce(op.add, themes + [color_theme])

    def validate_colors(self):
        """ensure that at least one of themes/colors is populated"""
        if not (self.themes or self.colors):
            raise ValueError('must set at least themes or colors')

    def validate_group(self) -> Group:
        if not self.group:
            raise ValueError('must set group')
        return self.group

    def __str__(self):
        return f'{self.colors}\n{self.themes}\n{self.group}'


pass_conf = click.make_pass_decorator(Config, ensure=True)


# ======================================================================================================================
# callbacks
# ======================================================================================================================

def _parse_groups(ctx, param, name_or_names) -> Group:
    if name_or_names == DEFAULT_GROUP:
        return lifx

    names = name_or_names.split(',')
    return reduce(op.add, (lifx[n] for n in names))


def _parse_colors(ctx, param, colors) -> List[Color]:
    if not colors:
        return []
    return [Colors[c.upper()] for c in colors.split(',')]


def _parse_themes(ctx, param, themes) -> List[Theme]:
    if not themes:
        return []
    return [Themes[t.lower()] for t in themes.split(',')]


def _parse_color_themes(ctx, param, color_themes) -> Optional[Theme]:
    if not color_themes:
        return None
    try:
        res = _parse_colors(ctx, param, color_themes)
        return routines.colors_to_theme(res)
    except KeyError:
        res = _parse_themes(ctx, param, color_themes)
        return res[0]


# ======================================================================================================================
# cli
# ======================================================================================================================


@click.group()
@click.option('-G', '--groups', 'group', callback=_parse_groups, default=DEFAULT_GROUP,
              help='csv of group or light name[s]')
@click.option('-C', '--colors', 'colors', callback=_parse_colors, default=None,
              help='csv of color[s] to apply')
@click.option('-T', '--themes', 'themes', callback=_parse_themes, default=None,
              help='csv of theme[s] to apply')
@click.option('-B', '--brightness-pct', default=100.,
              help='how bright, from 0.0-100.0, you want the lights to be')
@pass_conf
def cli_main(conf: Config, group, colors, themes, brightness_pct):
    conf.group = group
    conf.brightness_pct = brightness_pct
    conf.colors = colors
    conf.themes = themes


@cli_main.command()
@click.option('-l', '--light', is_flag=True, help='display info on all existing lights/groups')
@click.option('-c', '--color', is_flag=True, help='display info related to colors/themes')
@click.option('-d', '--debug', is_flag=True, help='display light debug info')
def info(light, color, debug):
    """display info about existing lights/groups and colors/themes"""
    if not (light or color or debug):
        light = color = True  # skip debug intentionally

    if light:
        echo(str(lifx))
        echo('\n'.join(map(str, lifx.auto_group().values())))

    if debug:
        echo('\n'.join(l.info_str() for l in lifx))

    if color:
        echo(80 * '=')
        echo('COLORS\n')
        echo('\n'.join(map(str, (c.color_str(name) for name, c in Colors))))

        echo('\n\n')
        echo(80 * '=')
        echo('THEMES\n')
        echo('\n\n'.join(map(str, (t.color_str(name) for name, t in Themes))))
        echo('\n')


@cli_main.command()
@click.option('--dot', callback=_parse_colors, default=None,
              help='set color for dot')
@click.option('--dash', callback=_parse_colors, default=None,
              help='set color for dash (will default to dot if not provided')
@click.argument('phrase', nargs=-1, required=True)
@pass_conf
def morse_code(conf: Config, dot, dash, phrase):
    """convert phrase into morse code"""
    phrase = ' '.join(phrase)
    echo(f'morse code: {phrase}')
    s = routines.MCSettings()

    if dot:
        dot = ColorPower(dot[0], 1)
    if dash:
        dash = ColorPower(dash[0], 1)

    dot = dot or s.dot
    dash = dash or dot or s.dash

    routines.morse_code(phrase, conf.group, routines.MCSettings(dot, dash))


@cli_main.command()
@click.option('-t', '--duration-secs', default=.5, help='how many secs for each color to appear')
@click.option('--smooth', is_flag=True, help='smooth transition between colors')
@pass_conf
def rainbow(conf: Config, duration_secs, smooth):
    """make lights cycle through rainbow color group"""
    routines.rainbow(conf.group, conf.color_theme or Themes.rainbow, duration_secs=duration_secs, smooth=smooth)


@cli_main.command(help=routines.light_eq.__doc__, short_help="control lights with the computer keyboard")
@pass_conf
def light_eq(conf: Config):
    routines.light_eq(conf.group, conf.color_theme)


@cli_main.command()
@click.option('-s', '--breath-secs', default=8)
@click.option('-m', '--duration-mins', default=20)
@click.option('--min-brightness-pct', default=30)
@click.option('--max-brightness-pct', default=60)
@pass_conf
def breathe(conf: Config, breath_secs, duration_mins, min_brightness_pct, max_brightness_pct):
    """make lights oscillate between darker and brighter """
    routines.breathe(conf.group, breath_secs, min_brightness_pct, max_brightness_pct, conf.color_theme,
                     duration_mins)


@cli_main.command()
@click.option('-s', '--blink-secs', default=.5)
@click.option('--how-long-secs', default=8)
@pass_conf
def blink_color(conf: Config, blink_secs, how_long_secs):
    """blink lights' colors"""
    routines.blink_color(conf.group, conf.color_theme, blink_secs, how_long_secs)


@cli_main.command()
@click.option('-s', '--blink-secs', default=.5)
@click.option('--how-long-secs', default=8)
@pass_conf
def blink_power(conf: Config, blink_secs, how_long_secs):
    """blink lights' power"""
    routines.blink_power(conf.group, blink_secs, how_long_secs)


@cli_main.command()
@click.option('-s', '--rotate-secs', default=60, help='how many seconds between each theme application')
@click.option('-m', '--duration-mins', default=20, help='how many minutes the command will run')
@click.option('-t', '--transition-secs', default=10, help='how many seconds to transition between themes')
@pass_conf
def cycle_themes(conf: Config, rotate_secs, duration_mins, transition_secs):
    """cycle through themes/colors passed in"""
    routines.cycle_themes(conf.group, *conf.themes, *conf.colors, rotate_secs=rotate_secs, duration_mins=duration_mins,
                          transition_secs=transition_secs)


@cli_main.command(help=routines.point_control.__doc__)
@click.option('-p', '--point-color-theme', default='YALE_BLUE',
              help='colors or theme of point to move around the lights',
              callback=_parse_color_themes)
@click.option('-b', '--base-color-theme', default=None,
              help='colors or theme for the background lights',
              callback=_parse_color_themes)
@click.option('-t', '--tail-secs', default=0.0,
              help='number of seconds for trailing lights to transition back to original color')
@click.option('-h', '--head-secs', default=0.0,
              help='number of seconds for next light to transition to new color')
@pass_conf
def point_control(conf: Config, point_color_theme: ColorTheme, base_color_theme: ColorTheme, tail_secs, head_secs):
    routines.point_control(conf.group,
                           conf.adjust_theme(point_color_theme), conf.adjust_theme(base_color_theme),
                           tail_delay_secs=tail_secs, head_delay_secs=head_secs)


@cli_main.command(help='run test on getch - press keys and see bytes')
@click.option('-s', '--separate-process', is_flag=True, default=False)
def getch_test(separate_process):
    _getch_test(separate_process)


@cli_main.command()
@pass_conf
def reset(conf: Config):
    """reset light colors to either DEFAULT or the first color you pass in"""
    (conf.group or lifx).set_theme(conf.color_theme or Theme.from_colors(conf.adjust_color(Colors.DEFAULT)))


@cli_main.command()
@pass_conf
def turn_off(conf: Config):
    """turn off lights in group"""
    conf.validate_group().turn_off()


@cli_main.command()
@pass_conf
def turn_on(conf: Config):
    """turn on lights in group"""
    conf.validate_group().turn_on()


@cli_main.command()
@pass_conf
def set_color_theme(conf: Config):
    """set group to colors/theme"""
    conf.validate_group().set_theme(conf.color_theme)


@cli_main.command()
@click.option('-k', '--kelvin-range', nargs=2, default=(2500, 4000), help='range of kelvin to select from [2500, 9000]')
@pass_conf
def set_whites(conf: Config, kelvin_range: Tuple[int, int]):
    """set lights to white in range of kelvin passed in"""
    g = conf.validate_group()
    l, h = (max(2500, min(v, 9000)) for v in kelvin_range)
    c = conf.adjust_color(Colors.DEFAULT)
    t = Theme.from_colors(*(c._replace(kelvin=k)
                            for k in random.choices(range(l, h + 1), k=len(g))))
    g.set_theme(t, power_on=False)


def __main():
    return cli_main()


if __name__ == '__main__':
    __main()
