from lifxlan import *
from random import randint, betavariate
from time import sleep

def main():
    lan = LifxLAN()
    tilechain_lights = lan.get_tilechain_lights()
    if len(tilechain_lights) != 0:
        t = lan.get_tilechain_lights()[0] #grab the first tilechain
        print("Selected TileChain light: {}".format(t.label))
        original_colors = t.get_tilechain_colors()
        (cols, rows) = t.get_canvas_dimensions()
        hue = 0
        rainbow_colors = []
        for row in range(rows):
            color_row = []
            for col in range(cols):
                color_row.append((hue, 65535, 65535, 4500))
                hue += int(65535.0/(cols*rows))
            rainbow_colors.append(color_row)

        t.project_matrix(rainbow_colors)

        duration_ms = 100

        try:
            while(True):
                rainbow_colors = cycle_row(rainbow_colors)
                t.project_matrix(rainbow_colors, duration_ms, rapid=True)
                sleep(max(duration_ms/2000.0, 0.05))
        except KeyboardInterrupt:
            t.set_tilechain_colors(original_colors)
            print("Done.")
    else:
        print("No TileChain lights found.")

def cycle_row(matrix):
    new_matrix = [matrix[-1]]
    for row in matrix[:-1]:
        new_matrix.append(row)
    return new_matrix

if __name__=="__main__":
    main()
