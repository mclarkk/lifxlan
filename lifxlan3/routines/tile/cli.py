import click

import lifxlan3.routines.tile.core as core
import lifxlan3.routines.tile.snek as snek_module


@click.group()
def cli_main():
    pass


@cli_main.command()
@click.option('-s', '--sleep-secs', default=1.0, help='how many seconds between different images')
@click.option('-t', '--in-terminal', is_flag=True, default=False, help='run in terminal')
@click.option('-d', '--duration_secs', default=30., help='how long to run')
@click.option('-b', '--as-ambiance', is_flag=True, default=False, help='run as ambiance')
def animate(sleep_secs, in_terminal, as_ambiance, duration_secs):
    """animate an image on tile lights or in terminal"""
    run_animate(sleep_secs, in_terminal, as_ambiance, duration_secs)


def run_animate(sleep_secs, in_terminal, as_ambiance, duration_secs):
    if as_ambiance:
        excluded_images = set()
        if not in_terminal:
            excluded_images = {'ff6_locke_full.png', 'mm.png', 'mario.png', 'snek.png', 'punch_out_mike.png',
                               'punch_out_lm.png'}
        im_fname = core.Images.get_random_image_name(excluded_images)
    else:
        im_str = '\n'.join(f'{i:3d}: {n}' for i, n in enumerate(core.Images.images))
        fn_idx = int(input(f'which image:\n{im_str}\n? '))
        im_fname = core.Images.images[fn_idx]
    core.animate(im_fname, sleep_secs=sleep_secs, in_terminal=in_terminal, how_long_secs=duration_secs)


@cli_main.command()
@click.option('-a', '--autoplay', is_flag=True, default=False, help='have snek autoplay')
@click.option('-t', '--in-terminal', is_flag=True, default=False, help='run in terminal')
@click.option('-b', '--as-ambiance', is_flag=True, default=False, help='run repeatedly as background')
def snek(autoplay, in_terminal, as_ambiance):
    """play the game of snek on tile lights or in terminal"""
    if as_ambiance:
        snek_module.run_as_ambiance()
    if autoplay:
        snek_module.autoplay(in_terminal)
    else:
        snek_module.play(in_terminal)


@cli_main.command()
@click.option('-r', '--rotate', is_flag=True, default=False, help='rotate based on tile_map')
def id_tiles(rotate):
    """help identify which tile is which"""
    core.id_tiles(rotate=rotate)


if __name__ == '__main__':
    cli_main()
