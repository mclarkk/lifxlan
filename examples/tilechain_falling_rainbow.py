from lifxlan import *
from random import randint
from time import sleep

def main():
    lan = LifxLAN()
    t = lan.get_device_by_name("Glider")
    #t = TileChain("d0:73:d5:33:14:4c", "10.0.0.8", verbose=False)
    num_tiles = 5
    (cols, rows) = t.get_canvas_dimensions(num_tiles)
    hue = 0
    rainbow_colors = []
    for row in range(rows):
        color_row = []
        for col in range(cols):
            color_row.append((hue, 65535, 1000, 4500))
            hue += int(65535.0/(cols*rows))
        rainbow_colors.append(color_row)

    t.project_matrix(rainbow_colors, num_tiles)

    duration_ms = 500

    while(True):
        rainbow_colors = cycle_row(rainbow_colors)
        t.project_matrix(rainbow_colors, num_tiles, duration_ms)
        sleep(duration_ms/2000.0)

def cycle_row(matrix):
    new_matrix = [matrix[-1]]
    for row in matrix[:-1]:
        new_matrix.append(row)
    return new_matrix

def get_random_color():
    return (randint(0,65535), randint(0,65535), randint(0,65535), randint(2500,9000))

if __name__=="__main__":
    main()
