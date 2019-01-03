from collections import defaultdict
from getch import getch

up, down, right, left = 0x41, 0x42, 0x43, 0x44
enter = 0xa
ctrl_r = 0x12
esc = 0x1b
l_bracket = 0x5b
one = 0x31
two = 0x32
semi = 0x3b


def parse_keyboard_inputs():
    """
    read and parse keyboard inputs

    handle multi-byte chars such as 'up', 'ctrl-r', and 'shift-left'

    this is a bit confusing.

    simple ascii chars will appear as one byte, like 0x41 -> 'A'

    some inputs, however, are multiple bytes, together at once.
    consider pressing 'up', it appears as [0x1b, 0x5b, 0x41], which is in fact [ESC, '[', 'A']]
    the below handles that by using some sort of state machine as represented by `tree`
    """

    def _create_tree():
        return defaultdict(_create_tree)

    # this tree manages multi-byte chars
    tree = _create_tree()
    mod1 = tree[esc][l_bracket]
    shift = mod1[one][semi][two]

    node = tree
    state = 0
    while True:
        try:
            c = ord(getch())
        except OverflowError:
            continue

        node = node.get(c)
        if node is mod1 or node is shift:
            state += 1
        if node is not None:
            continue

        yield c << (state * 8)

        node = tree
        state = 0


def getch_test():
    """run with this to see what chars lead to what bytes"""
    from lifxlan import exhaust
    import arrow

    def _getch_test():
        last_update = arrow.utcnow()
        while True:
            c = getch()
            if (arrow.utcnow() - last_update).total_seconds() > .05:
                print()
                last_update = arrow.utcnow()
            print('got', hex(ord(c)))

    exhaust(_getch_test())
