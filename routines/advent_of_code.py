import pickle
from concurrent.futures.process import ProcessPoolExecutor
from itertools import islice, combinations
from typing import NamedTuple
from functools import lru_cache, reduce


class Point(NamedTuple):
    x: int
    y: int


class Rect:
    def __init__(self, id, lower_left: Point, upper_right: Point):
        self.id = id
        self.ll = lower_left
        self.ur = upper_right

    @property
    @lru_cache(maxsize=None)
    def coords(self):
        return {(x, y)
                for x in range(self.ll.x, self.ur.x)
                for y in range(self.ll.y, self.ur.y)}

    @classmethod
    def from_str(cls, s):
        id_fld, _, coords, dims = s.split()
        id = int(id_fld[1:])
        x, y = map(int, coords[:-1].split(','))
        w, h = map(int, dims.split('x'))

        return cls(id, Point(x, y), Point(x + w, y + h))

    def __str__(self):
        return f'Rect({self.id}, ({self.ll}, {self.ur})'

    __repr__ = __str__

    def __and__(self, other):
        return self.coords & other.coords


null_rect = Rect(-1, Point(0, 0), Point(0, 0))


def read_input(fname):
    with open(f'/Users/xaxis/software/ipython37/inputs/{fname}') as f:
        return [Rect.from_str(l) for l in f]


def overlap(rect_pairs):
    return reduce(set().union, (r1 & r2 for r1, r2 in rect_pairs))


def chunks(iterable, size):
    it = iter(iterable)
    yield from iter(lambda: list(islice(it, size)), [])


def _run_distributed():
    rects = read_input(3)
    pool = ProcessPoolExecutor(4)
    combs = combinations(rects, 2)
    futures = [pool.submit(overlap, c) for c in chunks(combs, 10000)]
    return reduce(set().union, (f.result() for f in futures))


def non_overlapping():
    overlaps = _run_distributed()
    rects = read_input(3)
    for r in rects:
        if not r.coords & overlaps:
            print(r)
            return r


def __main():
    return non_overlapping()
    r = Rect.from_str('#123 @ 3,2: 5x4')
    print(len(r.coords))
    print(len(_run_distributed()))
    print('_____________')
    r1, r2, r3 = map(Rect.from_str, ('#1 @ 1,3: 4x4', '#2 @ 3,1: 4x4', '#3 @ 5,5: 2x2'))
    rs = r1, r2, r3
    print(rs)
    print(len(overlap(combinations(rs, 2))))
    print(r3.coords)


if __name__ == '__main__':
    __main()