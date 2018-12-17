from typing import NamedTuple
from enum import Enum







cart_chars = '^>v<'
cart_dir_map = dict(zip(cart_chars, '|-|-'))
valids = set(cart_chars + '+-|/\\')





class Turns(Enum):
    left = -1
    straight = 0
    right = 1
    
    def inc(self):
        turns = list(Turns)
        return turns[(turns.index(self) + 1) % len(turns)]

class Dirs(Enum):
    up = 0
    right = 1
    down = 2
    left = 3
    
    def turn_left(self):
        return self._turn_offset(-1)
        
    def turn_right(self):
        return self._turn_offset(1)
    
    def go_straight(self):
        return self._turn_offset(0)
    
    def _turn_offset(self, offset):
        dirs = list(Dirs)
        return dirs[(dirs.index(self) + offset) % len(dirs)]

turn_offset_map = {Turns.left: Dirs.turn_left,
                  Turns.straight: Dirs.go_straight,
                  Turns.right: Dirs.turn_right}
    
class Cart:
    def __init__(self, dir: Dirs):
        self.dir = dir
        self.next_turn = Turns.left
        
    def get_next_turn(self):
        t = self.next_turn
        self.next_turn = self.next_turn.inc()
        return t
        
    def __str__(self):
        return f'Cart: dir: {self.dir}, next_turn: {self.next_turn}'
    
    __repr__ = __str__
    
        
    

Dirs.up.turn_left().turn_left().turn_right().go_straight()







Turns.left.inc().inc().inc().inc().inc()







fn_test = './inputs/13.test'
fn_prod = './inputs/13'



def read_input(fn):
    grid, carts = {}, {}
    with open(fn) as f:
        for r, row in enumerate(f):
            for c, char in enumerate(row):
                if char not in valids:
                    continue
                if char in cart_chars:
                    carts[r, c] = Cart(Dirs(cart_chars.index(char)))
                    char = cart_dir_map[char]
                grid[r, c] = char
    return grid, carts
                    
        





class RC(NamedTuple):
    row: int
    col: int
        
    def __add__(self, other):
        return RC(self.row + other.row, self.col + other.col)



dir_offset_map = {Dirs.up: RC(-1, 0),
                 Dirs.right: RC(0, 1),
                 Dirs.down: RC(1, 0),
                 Dirs.left: RC(0, -1)}

maps = {'\\': {Dirs.up: Dirs.left,
               Dirs.left: Dirs.up,
              Dirs.right: Dirs.down,
              Dirs.down: Dirs.right},
       '/': {Dirs.up: Dirs.right,
            Dirs.right: Dirs.up,
            Dirs.left: Dirs.down,
            Dirs.down: Dirs.left}}

class CartPos(NamedTuple):
    rc: RC
    cart: Cart
    
    def move(self, char):
        d = self.cart.dir
        if char in '-|':
            new_dir = d
        elif char in '\\/':
            new_dir = maps[char][d]
        elif char == '+':
            new_dir = turn_offset_map[self.cart.get_next_turn()](d)
        
        self.cart.dir = new_dir
        return CartPos(self.rc + dir_offset_map[new_dir], self.cart)
            
            
    





# class Runner:
#     def __init__(self):
# #         self.grid, self.carts = read_input(fn_test + '2')
#         self.grid, self.carts = read_input(fn_prod)
    
#     def tick(self):
#         carts = sorted(self.carts.items())
#         new_carts = {}
#         for (r, c), cart in carts:
#             cp = CartPos(RC(r, c), cart)
            
#             cp = cp.move(self.grid[r, c])
#             if not self.check_collision(cp, new_carts):
#                 new_carts[cp.rc.row, cp.rc.col] = cp.cart
            
#         self.carts = {rc: new_carts[rc] for rc in sorted(new_carts)}
#         if len(self.carts) == 1:
#             print(self.carts)
#             raise Exception('done')
            
# #         print(self.carts)
            
#     def check_collision(self, cp: CartPos, new_carts):
#         if cp.rc in self.carts or cp.rc in new_carts:
#             print(f'collision occurred at {cp.rc}')
#             new_carts.pop(cp.rc, None)
#             self.carts.pop(cp.rc, None)
#             return True
            
        
        
class Runner:
    def __init__(self):
#         self.grid, self.carts = read_input(fn_test + '2')
        self.grid, self.carts = read_input(fn_prod)
    
    def tick(self):
        carts = dict(sorted(self.carts.items()))
        new_carts = {}
        keys = iter(list(carts.keys()))
        while carts:
            rc = RC(*next(keys))
            val = carts.pop(rc, None)
            if not val:
                continue
            cp = CartPos(rc, val)
            cp = cp.move(self.grid[rc])
            if not self.check_collision(cp, carts, new_carts):
                new_carts[cp.rc.row, cp.rc.col] = cp.cart

        self.carts = {rc: new_carts[rc] for rc in sorted(new_carts)}
        if len(self.carts) == 1:
            print(self.carts)
            raise Exception('done')
            
#         print(self.carts)
            
    @staticmethod
    def check_collision(cp: CartPos, carts, new_carts):
        if cp.rc in carts or cp.rc in new_carts:
            print(f'collision occurred at {cp.rc}')
            t = new_carts.pop(cp.rc, None)
            if t:
                print(f'removed {t} from new_carts')
            t = carts.pop(cp.rc, None)
            if t:
                print(f'removed {t} from carts')
            return True

r = Runner()

len(r.carts)





for _ in range(100000):
    r.tick()

r.tick()

r.carts
