import logging
import os
import time
from contextlib import suppress
from enum import Enum
from itertools import cycle, chain
from random import randint, choice, sample
from threading import Thread
from typing import NamedTuple, Deque, Dict, Set, Callable, Optional, Iterable

from lifxlan import Color, deque, Dir, Colors, Themes
from routines import parse_keyboard_inputs, dir_map, ColorTheme, colors_to_theme
from routines.tile.core import set_cm, translate
from routines.tile.tile_utils import RC, ColorMatrix, to_n_colors, a_star

dir_rc_map: Dict[Dir, RC] = {Dir.right: RC(0, 1),
                             Dir.left: RC(0, -1),
                             Dir.up: RC(-1, 0),
                             Dir.down: RC(1, 0)}

rc_dir_map: Dict[RC, Dir] = {v: k for k, v in dir_rc_map.items()}


class Cell(NamedTuple):
    pos: RC
    color: Color


def _rand_point(shape: RC) -> RC:
    return RC(randint(0, shape.r - 1), randint(0, shape.c - 1))


def _colors(c: ColorTheme):
    return cycle(colors_to_theme(c))


class SnekDead(Exception):
    """snek dead!"""


class SnekSucceeds(Exception):
    """snek win!"""


class Snek:
    def __init__(self, snek_color: Color, board_shape: RC, allow_wrap=True):
        self.colors = _colors(snek_color)
        self.board_shape = board_shape
        self.allow_wrap = allow_wrap

        self.sneque = self._init_sneque()

    def _init_sneque(self) -> Deque[Cell]:
        return deque([self._to_cell(_rand_point(self.board_shape))], maxlen=1)

    def _to_cell(self, pos: RC) -> Cell:
        return Cell(pos, next(self.colors))

    @property
    def positions(self) -> Set[RC]:
        return {c.pos for c in self.sneque}

    def grow(self, amount=1):
        """increase snek size by `amount`"""
        self.sneque = deque(self.sneque, maxlen=self.sneque.maxlen + amount)

    def move(self, dir: Dir):
        """move snek in `dir` direction"""
        self.sneque.append(self._to_cell(self.next_pos(dir)))

    def next_pos(self, dir: Dir):
        """calc next_pos and validate it"""
        return self._validate_pos(self.sneque[-1].pos + dir_rc_map[dir])

    def _validate_pos(self, pos: RC) -> RC:
        """check if snek ran into self or wall; return pos"""
        if pos in self and not pos == self.sneque[0].pos:
            raise SnekDead('snek ran into self :(')

        if self.allow_wrap:
            return pos % self.board_shape

        if not RC(0, 0) <= pos < self.board_shape:
            raise SnekDead('snek ran off the board :(')

        return pos

    def __contains__(self, pos: RC):
        return any(pos == c.pos for c in self.sneque)

    def __iter__(self):
        return iter(self.sneque)

    def __len__(self):
        return len(self.sneque)


def nothing(*_, **__):
    """do nothing"""


class Callbacks(NamedTuple):
    on_tick: Callable = nothing
    on_death: Callable = nothing
    on_success: Callable = nothing
    on_intro: Callable = nothing
    on_exit: Callable = nothing


class SnekGame:
    """play snek on your tile lights"""

    def __init__(self, snek_color: Color = Colors.GREEN,
                 background_color: ColorTheme = Colors.OFF,
                 food_color: ColorTheme = Colors.YALE_BLUE,
                 *,
                 snek_growth_amount=2,
                 shape=RC(16, 16),
                 tick_rate_secs=2.0,
                 callbacks: Callbacks = Callbacks()):
        self.board = self._init_board(background_color, shape)
        self._board_positions = set(RC(0, 0).to(shape))
        self.snek = Snek(snek_color, shape)
        self.food_colors = _colors(food_color)
        self.tick_rate_secs = tick_rate_secs
        self.callbacks = callbacks
        self.snek_growth_amount = snek_growth_amount

        self._set_food(init=True)
        self._dir: Dir = None
        self._prev_dir: Dir = None

    @staticmethod
    def _init_board(background_color, shape):
        colors = to_n_colors(*colors_to_theme(background_color), n=shape.r * shape.c)
        return ColorMatrix.from_colors(colors, shape)

    def _set_food(self, init=False):
        """
        set new food location for snek to eat when necessary

        will also check for win state
        """
        open_positions = self._board_positions - self.snek.positions
        if not init:
            open_positions -= {self.food.pos}
        if not open_positions:
            raise SnekSucceeds('YOU WIN!')
        self.food = Cell(choice(list(open_positions)), next(self.food_colors))

    @property
    def cm(self) -> ColorMatrix:
        cm = self.board.copy()
        for pos, color in chain([self.food], self.snek):
            cm[pos] = color
        return cm

    def run(self):
        """main event loop"""
        self._read_dir()
        self.callbacks.on_intro(self)
        try:
            with suppress(KeyboardInterrupt):
                while True:
                    self._on_tick()
                    self.callbacks.on_tick(self)
                    time.sleep(self.tick_rate_secs)
        except SnekDead:
            self.callbacks.on_death(self)
            raise
        except SnekSucceeds:
            self.callbacks.on_success(self)
            raise
        finally:
            self.callbacks.on_exit(self)
            os.system('reset')

    @property
    def score(self):
        """how big is snek"""
        return len(self.snek)

    def _read_dir(self):
        """store the most recently pushed dir here"""

        def f():
            for dir in parse_keyboard_inputs(dir_map, separate_process=True):
                if not self._prev_dir or dir != -self._prev_dir:
                    self._dir = dir

        Thread(target=f, daemon=True).start()

    def _on_tick(self):
        """update board, snek, food, etc as needed"""
        if self._dir is None:
            return

        self._prev_dir = self._dir
        next_pos = self.snek.next_pos(self._dir)
        if next_pos == self.food.pos:
            self.snek.grow(self.snek_growth_amount)
            self._set_food()

        self.snek.move(self._dir)


class AutoSnekGame(SnekGame):
    def _read_dir(self):
        """disable reading of directions from keyboard"""

    def _get_directions(self, prev_food_pos: Optional[RC]) -> Iterable[Dir]:
        start = prev_food_pos or self.snek.sneque[-1].pos
        goal = self.food.pos
        impassable = self.snek.positions
        if prev_food_pos:
            impassable.add(prev_food_pos)
        args = self.board, start, goal, impassable
        positions = a_star(*args, allow_wrap=True)
        try:
            return (rc_dir_map[p1 - p0] for p0, p1 in zip(positions, positions[1:]))
        except TypeError as e:
            raise SnekDead('snek ran into dead end!') from e

    def _set_food(self, init=False):
        prev_food_pos = None
        if not init:
            prev_food_pos = self.food.pos
        super()._set_food(init)
        self._dirs = iter(self._get_directions(prev_food_pos))

    def _on_tick(self):
        try:
            self._dir = next(self._dirs)
        except StopIteration as e:
            raise SnekDead from e
        super()._on_tick()


# ======================================================================================================================
# callbacks
# ======================================================================================================================

def terminal_tick(game: SnekGame):
    os.system('clear')
    print(game.cm.color_str)
    print(game.snek.sneque.maxlen)


def lights_tick(game: SnekGame):
    set_cm(game.cm, strip=False)


def lights_intro(game: SnekGame):
    # return
    translate('./imgs/snek.png', split=False, dir=Dir.left, sleep_secs=.1, n_iterations=1)

    time.sleep(.3)


def on_death(game: SnekGame):
    explode()
    print('death')
    print(f'score: {game.score}')


def terminal_on_death(game: SnekGame):
    print('death')
    print(f'score: {game.score}')


def on_success(game: SnekGame):
    print('WIN!')
    print(f'score: {game.score}')


def propagate(cm: ColorMatrix, base: Color, explosion: Color):
    current = cm.find_all(explosion)
    offsets = RC(-1, -1), RC(1, 1), RC(-1, 1), RC(1, -1)
    for c_rc in current:
        for o in offsets:
            cm[c_rc + o] = explosion
    for c_rc in current:
        cm[c_rc] = base
    return cm


def explode(base_color: Color = Colors.STEELERS_RED,
            explosion_color: Color = Colors.COLD_WHITE, in_terminal=False):
    colors = to_n_colors(base_color.r_brightness(20000), n=256)
    cm = ColorMatrix.from_colors(colors, RC(16, 16))
    start, end = RC(7, 7), RC(9, 9)
    cm[start] = cm[end] = explosion_color
    # for rc in start.to(end):
    #     cm[rc] = explosion_color

    # expand
    with suppress(IndexError):
        for _ in range(10):
            set_cm(cm, strip=False, in_terminal=in_terminal)
            propagate(cm, base_color, explosion_color)
            time.sleep(.1)

    if in_terminal:
        return

    # fill white
    for offset in range(8):
        s, e = start - RC(offset, offset), end + RC(offset, offset)
        for rc in s.to(e):
            cm[rc] = explosion_color
        set_cm(cm, strip=False, in_terminal=in_terminal)
        time.sleep(.1)

    # fade to black
    colors = to_n_colors(Colors.OFF, n=256)
    cm = ColorMatrix.from_colors(colors, RC(16, 16))
    set_cm(cm, strip=False, duration_msec=3000)


def for_talk():
    g = AutoSnekGame(shape=RC(16, 16), tick_rate_secs=.05,
                     callbacks=Callbacks(lights_tick, on_death, on_success, lights_intro),
                     snek_color=Colors.GREEN,
                     # snek_color=Themes.rainbow,
                     background_color=Colors.SNES_DARK_GREY._replace(brightness=6554),
                     food_color=Colors.YALE_BLUE)

    g.run()


def run_as_ambiance():
    background = Colors.SNES_DARK_GREY._replace(brightness=6554)
    color_options = list(Colors) + list(Themes)

    while True:
        food_c, snek_c = (o[1] for o in sample(color_options, 2))
        with suppress(SnekDead):
            g = AutoSnekGame(shape=RC(16, 16), tick_rate_secs=1,
                             callbacks=Callbacks(lights_tick, on_death, on_success),
                             food_color=food_c,
                             snek_color=snek_c,
                             background_color=background)
            g.run()


def autoplay(in_terminal=False):
    if in_terminal:
        g = AutoSnekGame(shape=RC(16, 16), tick_rate_secs=.05,
                         callbacks=Callbacks(terminal_tick, terminal_on_death, on_success),
                         background_color=Colors.SNES_LIGHT_GREY, snek_color=Colors.COPILOT_BLUE_GREEN,
                         food_color=Colors.SNES_LIGHT_PURPLE, snek_growth_amount=2)
    else:
        g = AutoSnekGame(shape=RC(16, 16), tick_rate_secs=.05,
                         callbacks=Callbacks(lights_tick, on_death, on_success, lights_intro),
                         snek_color=Colors.GREEN,
                         # snek_color=Themes.july_4th,
                         background_color=Colors.SNES_DARK_GREY._replace(brightness=6554),
                         food_color=Colors.YALE_BLUE)
    g.run()


def play(in_terminal=False):
    if in_terminal:
        g = SnekGame(shape=RC(16, 16), tick_rate_secs=.2,
                     callbacks=Callbacks(terminal_tick, terminal_on_death, on_success),
                     background_color=Colors.SNES_LIGHT_GREY, snek_color=Colors.COPILOT_BLUE_GREEN,
                     food_color=Colors.SNES_LIGHT_PURPLE, snek_growth_amount=2)
    else:
        g = SnekGame(shape=RC(16, 16), tick_rate_secs=.2,
                     callbacks=Callbacks(lights_tick, on_death, on_success, lights_intro),
                     snek_color=Colors.GREEN,
                     # snek_color=Themes.july_4th,
                     background_color=Colors.SNES_DARK_GREY._replace(brightness=6554),
                     food_color=Colors.YALE_BLUE)
    g.run()


def __main():
    return run_as_ambiance()
    # return for_talk()
    # return play()
    # g = AutoSnekGame(shape=RC(16, 16), tick_rate_secs=.05,
    #                  callbacks=Callbacks(terminal_tick, terminal_on_death, on_success),
    #                  background_color=Colors.SNES_LIGHT_GREY, snek_color=Colors.COPILOT_BLUE_GREEN,
    #                  food_color=Colors.SNES_LIGHT_PURPLE, snek_growth_amount=2)
    # g = SnekGame(shape=RC(16, 16), tick_rate_secs=.05,
    #              callbacks=Callbacks(lights_cb, on_death, on_success, lights_intro),
    #              background_color=Colors.OFF, snek_color=Colors.GREEN)
    g = AutoSnekGame(shape=RC(16, 16), tick_rate_secs=.05,
                     callbacks=Callbacks(lights_tick, on_death, on_success, lights_intro),
                     snek_color=Colors.GREEN,
                     # snek_color=Themes.july_4th,
                     background_color=Colors.SNES_DARK_GREY._replace(brightness=6554),
                     food_color=Colors.YALE_BLUE)
    g.run()


if __name__ == '__main__':
    __main()
