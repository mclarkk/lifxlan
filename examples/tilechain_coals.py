from lifxlan import *
from random import randint, betavariate
from time import sleep


def main():
    lan = LifxLAN()
    tilechain_lights = lan.get_tilechain_lights()
    if len(tilechain_lights) != 0:
        t = lan.get_tilechain_lights()[0]  # grab the first tilechain
        print("Selected TileChain light: {}".format(t.get_label()))
        original_colors = t.get_tilechain_colors()
        (cols, rows) = t.get_canvas_dimensions()
        hue = 0
        coal_colors = []
        for row in range(rows):
            color_row = []
            for col in range(cols):
                color_row.append(get_fire_color())
                hue += int(65535.0 / (cols * rows))
            coal_colors.append(color_row)

        t.project_matrix(coal_colors)

        duration_ms = 400

        try:
            while True:
                proportion_change = 0.2
                sample_size = int((rows * cols) * proportion_change)
                if sample_size % 2 == 1:
                    sample_size = int(sample_size - 1)
                col_samples = [randint(0, cols - 1) for i in range(sample_size)]
                row_samples = [randint(0, rows - 1) for i in range(sample_size)]
                for i in range(0, sample_size):
                    coal_colors[row_samples[i]][col_samples[i]] = get_fire_color()
                t.project_matrix(coal_colors, duration_ms, rapid=True)
                sleep(max(duration_ms / 2000.0, 0.05))
        except KeyboardInterrupt:
            t.set_tilechain_colors(original_colors)
            print("Done.")
    else:
        print("No TileChain lights found.")


def get_fire_color():
    return (
        int(800 + (5000 * betavariate(0.2, 0.9))),
        randint(60000, 65535),
        int(65535 * betavariate(0.05, 1)),
        randint(2500, 3500),
    )


if __name__ == "__main__":
    main()
