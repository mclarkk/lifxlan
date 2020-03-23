from lifxlan3 import init_log, Dir, GridLight, Group, enlighten_grid

__author__ = 'acushner'

log = init_log(__name__)


def init_grid(group: Group):
    # CREATE LIGHTS
    lr1 = GridLight('living room 1')
    lr2 = GridLight('living room 2')
    lr3 = GridLight('living room 3')
    lr4 = GridLight('living room 4')

    buffet = GridLight('buffet')
    floor = GridLight('floor')

    dr1 = GridLight('dining room 1')
    dr2 = GridLight('dining room 2')

    k1 = GridLight('kitchen 1')
    k2 = GridLight('kitchen 2')
    k3 = GridLight('kitchen 3')
    k4 = GridLight('kitchen 4')

    cs1 = GridLight('creative space 1')
    cs2 = GridLight('creative space 2')
    cs3 = GridLight('creative space 3')
    cs4 = GridLight('creative space 4')

    m1 = GridLight('master 1')
    m2 = GridLight('master 2')

    _diagram = \
        """
           buffet
        lr4 lr1   dr1   k4 k1   cs4 cs1
        lr3 lr2   dr2   k3 k2   cs3 cs2
               floor
        """
    # DOWNSTAIRS ASSOCIATIONS
    buffet[Dir.up] = floor
    buffet[Dir.left] = lr4
    buffet[Dir.right] = lr1

    floor[Dir.left] = lr3
    floor[Dir.right] = lr2

    lr4[Dir.right] = lr1
    lr4[Dir.down] = lr3

    lr3[Dir.right] = lr2

    lr1[Dir.up] = buffet
    lr1[Dir.down] = lr2
    lr1[Dir.right] = dr1

    lr2[Dir.down] = floor
    lr2[Dir.right] = dr2

    dr1[Dir.down] = dr2
    dr1[Dir.right] = k4
    dr2[Dir.right] = k3

    k4[Dir.right] = k1
    k4[Dir.down] = k3

    k3[Dir.right] = k2

    k1[Dir.down] = k2
    k1[Dir.right] = cs4

    k2[Dir.right] = cs3

    cs4[Dir.right] = cs1
    cs4[Dir.down] = cs3

    cs1[Dir.down] = cs2

    cs3[Dir.right] = cs2
    # to wrap around:
    # k1[Dir.right] = lr4
    #
    # k2[Dir.right] = lr3

    # UPSTAIRS ASSOCIATIONS
    m1[Dir.right] = m2
    if group:
        enlighten_grid(group)


