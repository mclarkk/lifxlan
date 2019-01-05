import time
from collections import defaultdict
from contextlib import suppress
from multiprocessing import Process, Queue, Pipe, connection

up, down, right, left = 0x41, 0x42, 0x43, 0x44
enter = 0xa
ctrl_r = 0x12
esc = 0x1b
l_bracket = 0x5b
one = 0x31
two = 0x32
semi = 0x3b


def _getch_ord() -> int:
    """
    return ordinal from getch

    ignore OverflowError exceptions
    """
    from getch import getch
    while True:
        with suppress(OverflowError):
            return ord(getch())


def _getch_wrapper(separate_process):
    """handle whether or not `getch` is run in separate process"""
    if separate_process:
        yield from _getch_sep()
    else:
        yield from iter(_getch_ord, object())


def _getch_sep():
    """get chars in separate process when having multithreading issues"""
    reader, writer = Pipe(False)

    def _getch_helper():
        while True:
            writer.send(_getch_ord())

    t = Process(target=_getch_helper, daemon=True)
    t.start()

    while True:
        c = reader.recv()
        yield c


def parse_keyboard_inputs(*, separate_process=False):
    """
    read and parse keyboard inputs

    handle multi-byte chars such as 'up', 'ctrl-r', and 'shift-left'

    this is a bit confusing.

    simple ascii chars will appear as one byte, like 0x41 -> 'A'

    some inputs, however, are multiple bytes, together at once.
    consider pressing 'up', it appears as [0x1b, 0x5b, 0x41], which is in fact [ESC, '[', 'A']]
    the below handles that by using some sort of state machine as represented by `tree`

    NOTE: set `separate_process` to True if you're having trouble with multithreading and getch
    """

    _create_tree = lambda: defaultdict(_create_tree)

    # this tree manages multi-byte chars
    tree = _create_tree()
    mod1 = tree[esc][l_bracket]
    shift = mod1[one][semi][two]

    node = tree
    state = 0

    for c in _getch_wrapper(separate_process):
        node = node.get(c)
        if node is mod1 or node is shift:
            state += 1
        if node is not None:
            continue

        yield c << (state * 8)

        node = tree
        state = 0


def getch_test(separate_process=False):
    """run with this to see what inputs lead to what bytes"""
    from lifxlan import exhaust
    import arrow

    def _getch_test():
        last_update = arrow.utcnow()
        for c in _getch_wrapper(separate_process):
            if (arrow.utcnow() - last_update).total_seconds() > .05:
                print()
                last_update = arrow.utcnow()
            print('got', hex(c))

    exhaust(_getch_test())
