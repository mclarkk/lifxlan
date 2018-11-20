from lifxlan import *
from random import randint, choice
from time import sleep
from copy import deepcopy


def main():
    lan = LifxLAN()
    tilechain_lights = lan.get_tilechain_lights()
    if len(tilechain_lights) != 0:
        tile_chain = lan.get_tilechain_lights()[0]  # grab the first tilechain
        print("Selected TileChain light: {}".format(tile_chain.label))
        (cols, rows) = tile_chain.get_canvas_dimensions()
        original_colors = tile_chain.get_tilechain_colors()

        background_colors = set_background(cols, rows)
        tile_chain.project_matrix(background_colors, 2000)

        dots = []
        max_dots = 50
        duration_ms = 150
        dot_rate = 0.1

        matrix = deepcopy(background_colors)

        try:
            while True:
                dot = [choice(range(rows)), choice(range(cols))]
                dots.append(dot)

                if len(dots) > max_dots:
                    old_dot = dots.pop(0)
                    matrix[int(old_dot[0])][int(old_dot[1])] = background_colors[int(old_dot[0])][int(old_dot[1])]

                matrix[int(dot[0])][int(dot[1])] = get_random_saturated_color()
                #Catch exceptions when the computer sleeps so we can resume when we wake
                try:
                    tile_chain.project_matrix(matrix, duration_ms, rapid=True)
                except:
                    pass
                sleep(dot_rate)
        except KeyboardInterrupt:
                tile_chain.set_tilechain_colors(original_colors)
                print("Done.")
    else:
            print("No TileChain lights found.")


def get_random_saturated_color():
    return randint(0, 65535), 65535, randint(0, 65535), 3000


def set_background(cols, rows):
    hue = 0
    background_colors = []
    for row in range(rows):
        color_row = []
        for col in range(cols):
            color_row.append((hue, 65535, 2000, 4900))
            hue += int(65535.0 / (cols * rows))
        background_colors.append(color_row)
    return background_colors


if __name__ == "__main__":
    main()
