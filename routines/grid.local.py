import time

from lifxlan import init_log, grid, Dir, GridLight, LifxLAN, Colors
from lifxlan.grid import enlighten_grid

__author__ = 'acushner'

log = init_log(__name__)

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

m1 = GridLight('master 1')
m2 = GridLight('master 2')

_diagram = \
    """
      buffet
    lr4 lr1   dr1   k4 k1
    lr3 lr2   dr2   k3 k2
       floor
    """
# downstairs
buffet[Dir.up] = floor
buffet[Dir.left] = lr4
buffet[Dir.right] = lr1

floor[Dir.left] = lr3
floor[Dir.right] = lr2

lr4[Dir.up] = lr3
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
k1[Dir.right] = lr4

k2[Dir.right] = lr3

# upstairs
m1[Dir.right] = m2

for l in grid.values():
    print(l.name)
    print(l.neighbors)
    print(80 * '=')

l = lr4
for _ in range(8):
    print(l)
    l = l.move(Dir.right)


def with_lights():
    lifx = LifxLAN()
    enlighten_grid(lifx)
    gl = grid['master 1']
    for _ in range(8):
        print(gl)
        with gl.light.reset_to_orig(duration=0):
            gl.light.set_color(Colors.YALE_BLUE)
            time.sleep(.4)
            gl = gl.move(Dir.right)


def __main():
    with_lights()
    pass


if __name__ == '__main__':
    __main()
