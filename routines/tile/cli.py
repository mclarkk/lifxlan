import click

import routines.tile.core as core


@click.group()
def cli_main():
    pass


@cli_main.command()
@click.option('-s', '--sleep-secs', default=2.0, help='how many seconds between different images')
@click.option('-t', '--in-terminal', is_flag=True, default=False, help='run in terminal')
def animate(sleep_secs, in_terminal):
    """animate an image"""
    im_str = '\n'.join(f'{i}: {n}' for i, n in enumerate(core.images))
    fn_idx = int(input(f'which image:\n{im_str}\n? '))
    core.animate(f'./imgs/{core.images[fn_idx]}', sleep_secs=sleep_secs, in_terminal=in_terminal)


@cli_main.command()
@click.option('-r', '--rotate', is_flag=True, default=False, help='rotate based on tile_map')
def id_tiles(rotate):
    core.id_tiles(rotate)

if __name__ == '__main__':
    cli_main()
