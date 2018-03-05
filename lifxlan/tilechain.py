import os

from .device import WorkflowException
from .light import Light
from .msgtypes import GetTileState64, StateTileState64, SetTileState64, GetDeviceChain, StateDeviceChain, SetUserPosition

class TileChain(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        super(TileChain, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)

    # returns information about all tiles
    def get_tile_info(self):
        response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
        tiles = []
        for tile in response.tile_devices:
            t = Tile(tile["user_x"], tile["user_y"], tile["width"], tile["height"], tile["device_version_vendor"], tile["device_version_product"], tile["device_version_version"], tile["firmware_build"], tile["firmware_version"])
            tiles.append(t)
        return tiles[:response.total_count]

    # should return the number of tiles in the chain...right?
    def get_tile_count(self):
        response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
        self.total_count = response.total_count
        return self.total_count

    # danger zoooooone
    def set_tile_coordinates(self, tile_index, x, y):
        self.req_with_ack(SetUserPosition, {"tile_index": tile_index, "reserved": 0, "user_x": x, "user_y": y})

    def get_tile_colors(self, start_index, tile_count=1, x=0, y=0, width=8):
        # ADD VALIDATION HERE SOMEDAY MAYBE

        colors = []
        for i in range(tile_count):
            payload = {"tile_index": start_index + i,
                       "length": 1,
                       "reserved": 0,
                       "x": x,
                       "y": y,
                       "width": width}
            response = self.req_with_resp(GetTileState64, StateTileState64, payload)
            colors.append(response.colors)
        return colors

    def set_tile_colors(self, start_index, colors, duration=0, tile_count=1, x=0, y=0, width=8, rapid=False):
        payload = {"tile_index": start_index,
                   "length": tile_count,
                   "colors": colors,
                   "duration": duration,
                   "reserved": 0,
                   "x": x,
                   "y": y,
                   "width": width}
        self.req_with_ack(SetTileState64, payload)

    # shouldn't need the num_tiles parameter once we can correctly get num tiles
    def recenter_coordinates(self, num_tiles):
        x_vals, y_vals = self.get_xy_vals(num_tiles)
        x_vals = self.center_axis(x_vals)
        y_vals = self.center_axis(y_vals)
        centered_coordinates = list(zip(x_vals, y_vals))
        for (tile_index, (user_x, user_y)) in enumerate(centered_coordinates):
            self.set_tile_coordinates(tile_index, user_x, user_y)

    # ETC. for the num_tiles
    def project_matrix(self, hsvk_matrix, num_tiles, duration = 0, default_color = (0, 0, 0, 0)):
        canvas_x, canvas_y = self.get_canvas_dimensions(num_tiles)
        matrix_x = len(hsvk_matrix[0])
        matrix_y = len(hsvk_matrix)
        if (matrix_x != canvas_x) or (matrix_y != canvas_y):
            print("Warning: TileChain canvas wants a {} x {} matrix, but given matrix is {} x {}.".format(canvas_x, canvas_y, matrix_x, matrix_y))

        tile_width = 8 # hardcoded, argh
        tile_height = 8
        tile_map = self.get_tile_map(num_tiles)
        tile_colors = [[default_color for i in range(tile_width * tile_height)] for j in range(num_tiles)]

        rows = canvas_y
        cols = canvas_x
        for row in range(rows):
            for col in range(cols):
                if tile_map[row][col] != 0:
                    (tile_num, color_num) = tile_map[row][col]
                    tile_colors[tile_num][color_num] = hsvk_matrix[row][col]

        for (i, tile_color) in enumerate(tile_colors):
           self.set_tile_colors(i, tile_color, duration=duration)

    ### HELPER FUNCTIONS

    # will be able to remove num_tiles once we can get it programmatically
    def get_xy_vals(self, num_tiles):
        tiles = self.get_tile_info()
        x_vals = []
        y_vals = []
        for tile in tiles[:num_tiles]:
            x_vals.append(tile.user_x)
            y_vals.append(tile.user_y)
        x_vals = self.center_axis(x_vals)
        y_vals = self.center_axis(y_vals)
        return x_vals, y_vals

    def center_axis(self, axis_vals):
        if 0.0 not in axis_vals:
            smallest_val = min([abs(val) for val in axis_vals])
            closest_val = 0.0
            for val in axis_vals:
                if abs(val) == smallest_val:
                    closest_val = val
            axis_vals = [(-1*closest_val) + val for val in axis_vals]
        return axis_vals

    # all become non-negative -- shifts (0, 0) to the left/top
    def shift_axis_upper_left(self, axis_vals, is_y = False):
        if is_y:
            axis_vals = [-1*val for val in axis_vals]
        smallest_val = min(axis_vals)
        axis_vals = [(-1*smallest_val) + val for val in axis_vals]
        return axis_vals

    # will be able to remove num_tiles once we can get it programmatically
    def get_canvas_dimensions(self, num_tiles):
        x_vals, y_vals = self.get_xy_vals(num_tiles)
        min_x = min(x_vals)
        max_x = max(x_vals)
        min_y = min(y_vals)
        max_y = max(y_vals)
        x_tilespan = (max_x - min_x) + 1
        y_tilespan = (max_y - min_y) + 1
        tile_width = 8 #TO DO: get these programmatically for each light from the tile info
        tile_height = 8 #TO DO: get these programmatically for each light from the tile info
        canvas_x = int(x_tilespan * tile_width)
        canvas_y = int(y_tilespan * tile_height)
        return (canvas_x, canvas_y)

    # THIS DOESN'T WORK WITH GAPS
    def get_tile_map(self, num_tiles):
        tile_width = 8 #TO DO: get these programmatically for each light from the tile info
        tile_height = 8 #TO DO: get these programmatically for each light from the tile info
        (x, y) = self.get_canvas_dimensions(num_tiles)
        #print(x, y)
        tile_map = [[0 for i in range(x)] for j in range(y)]

        tiles = self.get_tile_info()
        x_vals, y_vals = self.get_xy_vals(num_tiles)
        x_vals = self.shift_axis_upper_left(x_vals)
        y_vals = self.shift_axis_upper_left(y_vals, is_y=True)

        for i in range(num_tiles):
            tile = tiles[i]
            x_start_tilespan = x_vals[i]
            y_start_tilespan = y_vals[i]
            #print(i, x_start_tilespan, y_start_tilespan)
            x_start_pixel = int(x_start_tilespan * tile_width)
            y_start_pixel = int(y_start_tilespan * tile_height)
            for j in range(y_start_pixel, y_start_pixel + tile_width):
                for k in range(x_start_pixel, x_start_pixel + tile_height):
                    j0 = j - y_start_pixel
                    k0 = k - x_start_pixel
                    tile_map[j][k] = (i, (j0*tile_width + k0))

        #for row in tile_map:
        #    print(row)
        self.tile_map = tile_map
        return self.tile_map


class Tile(object):
    def __init__(self, user_x, user_y, width=8, height=8, device_version_vendor=None, device_version_product=None, device_version_version=None, firmware_build=None, firmware_version=None):
        super(Tile, self).__init__()
        self.user_x = user_x
        self.user_y	= user_y
        self.width = width
        self.height = height
        self.device_version_vendor = device_version_vendor
        self.device_version_product = device_version_product
        self.device_version_version = device_version_version
        self.firmware_build = firmware_build
        self.firmware_version = firmware_version

    def __str__(self):
        s = "\nTile at {}, {}:".format(self.user_x, self.user_y)
        s += "\n  User X: " + str(self.user_x)
        s += "\n  User Y: " + str(self.user_y)
        s += "\n  Width: " + str(self.width)
        s += "\n  Height: " + str(self.height)
        s += "\n  Device Version Vendor: " + str(self.device_version_vendor)
        s += "\n  Device Version Product: " + str(self.device_version_product)
        s += "\n  Device Version Version: " + str(self.device_version_version)
        s += "\n  Firmware Build: " + str(self.firmware_build)
        s += "\n  Firmware Version: " + str(self.firmware_version)
        return s
