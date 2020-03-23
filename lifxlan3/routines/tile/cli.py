import click

import lifxlan3.routines.tile.core as core
import lifxlan3.routines.tile.snek as snek_module


@click.group()
def cli_main():
    pass


@cli_main.command()
@click.option('-s', '--sleep-secs', default=2.0, help='how many seconds between different images')
@click.option('-t', '--in-terminal', is_flag=True, default=False, help='run in terminal')
def animate(sleep_secs, in_terminal):
    """animate an image on tile lights or in terminal"""
    im_str = '\n'.join(f'{i:3d}: {n}' for i, n in enumerate(core.images))
    fn_idx = int(input(f'which image:\n{im_str}\n? '))
    core.animate(f'./imgs/{core.images[fn_idx]}', sleep_secs=sleep_secs, in_terminal=in_terminal)


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
