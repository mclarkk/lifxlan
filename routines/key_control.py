from lifxlan import init_log, Group
from getch import getch

__author__ = 'acushner'

log = init_log(__name__)

from routines import ColorTheme, colors_to_themes


def control(lifx: Group, colors: ColorTheme):
    theme = colors_to_themes(colors)
    with lifx.reset_to_orig():

        pass


def __main():
    pass


if __name__ == '__main__':
    __main()
