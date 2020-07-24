import random

from .errors import WorkflowException, InvalidParameterException
from .light import Light
from .msgtypes import GetTileState64, StateTileState64, SetTileState64, GetDeviceChain, StateDeviceChain, SetUserPosition, SetTileEffect, GetTileEffect, StateTileEffect
from threading import Thread

class TileChain(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=random.randrange(2, 1 << 32), verbose=False):
        super(TileChain, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)
        self.tile_info = None
        self.tile_count = None
        self.tile_map = None
        self.canvas_dimensions = None
        self.get_tile_info()
        self.get_tile_map()
        self.get_canvas_dimensions()

    # returns information about all tiles
    def get_tile_info(self, refresh_cache=False):
        if (self.tile_info == None) or (refresh_cache == True):
            response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
            tiles = []
            for tile in response.tile_devices:
                t = Tile(tile["user_x"], tile["user_y"], tile["width"], tile["height"], tile["device_version_vendor"], tile["device_version_product"], tile["device_version_version"], tile["firmware_build"], tile["firmware_version"])
                tiles.append(t)
            self.tile_info = tiles[:response.total_count]
            self.tile_count = response.total_count
        return self.tile_info

    def get_tile_count(self, refresh_cache=False):
        if (self.tile_count == None) or (refresh_cache == True):
            response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
            self.tile_count = response.total_count
        return self.tile_count

    def get_tile_colors(self, start_index, tile_count=1, x=0, y=0, width=8):
        if (start_index < 0) or (start_index >= self.tile_count):
            raise InvalidParameterException("{} is not a valid start_index for TileChain with {} tiles.".format(start_index, self.tile_count))

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

    def get_tilechain_colors(self):
        tilechain_colors = []
        for i in range(self.tile_count):
            tile_colors = self.get_tile_colors(i)
            tilechain_colors.append(tile_colors[0])
        return tilechain_colors

    def set_tile_colors(self, start_index, colors, duration=0, tile_count=1, x=0, y=0, width=8, rapid=False):
        if (start_index < 0) or (start_index >= self.tile_count):
            raise InvalidParameterException("{} is not a valid start_index for TileChain with {} tiles.".format(start_index, self.tile_count))

        payload = {"tile_index": start_index,
                   "length": tile_count,
                   "colors": colors,
                   "duration": duration,
                   "reserved": 0,
                   "x": x,
                   "y": y,
                   "width": width}
        if not rapid:
            self.req_with_ack(SetTileState64, payload)
        else:
            self.fire_and_forget(SetTileState64, payload, num_repeats=1)

    def set_tilechain_colors(self, tilechain_colors, duration=0, rapid=False):
        threads = []
        for i in range(self.tile_count):
            t = Thread(target = self.set_tile_colors, args = ((i, tilechain_colors[i], duration, 1, 0, 0, 8, rapid)))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def recenter_coordinates(self):
        num_tiles = self.get_tile_count()
        x_vals, y_vals = self.get_xy_vals()
        x_vals = self.center_axis(x_vals)
        y_vals = self.center_axis(y_vals)
        centered_coordinates = list(zip(x_vals, y_vals))
        for (tile_index, (user_x, user_y)) in enumerate(centered_coordinates):
            self.set_tile_coordinates(tile_index, user_x, user_y)

    def project_matrix(self, hsvk_matrix, duration = 0, rapid=False):
        num_tiles = self.get_tile_count()
        canvas_x, canvas_y = self.get_canvas_dimensions()
        matrix_x = len(hsvk_matrix[0])
        matrix_y = len(hsvk_matrix)
        if (matrix_x != canvas_x) or (matrix_y != canvas_y):
            raise InvalidParameterException("Warning: TileChain canvas wants a {} x {} matrix, but given matrix is {} x {}.".format(canvas_x, canvas_y, matrix_x, matrix_y))

        tile_width = 8 # hardcoded, argh
        tile_height = 8
        default_color = (0, 0, 0, 0)
        tile_map = self.get_tile_map()
        tile_colors = [[default_color for i in range(tile_width * tile_height)] for j in range(num_tiles)]

        rows = canvas_y
        cols = canvas_x
        for row in range(rows):
            for col in range(cols):
                if tile_map[row][col] != 0:
                    (tile_num, color_num) = tile_map[row][col]
                    tile_colors[tile_num][color_num] = hsvk_matrix[row][col]

        threads = []
        for (i, tile_color) in enumerate(tile_colors):
            t = Thread(target = self.set_tile_colors, args = ((i, tile_color, duration, 1, 0, 0, 8, rapid)))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    ### HELPER FUNCTIONS

    # danger zoooooone
    def set_tile_coordinates(self, tile_index, x, y):
        self.req_with_ack(SetUserPosition, {"tile_index": tile_index, "reserved": 0, "user_x": x, "user_y": y})
        # update cached information
        self.get_tile_info(refresh_cache=True)
        self.get_tile_map(refresh_cache=True)
        self.get_canvas_dimensions(refresh_cache=True)

    def get_xy_vals(self):
        tiles = self.get_tile_info()
        num_tiles = self.get_tile_count()
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

    def get_canvas_dimensions(self, refresh_cache=False):
        if (self.canvas_dimensions == None) or (refresh_cache == True):
            x_vals, y_vals = self.get_xy_vals()
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
            self.canvas_dimensions = (canvas_x, canvas_y)
        return self.canvas_dimensions

    def get_tile_map(self, refresh_cache=False):
        if (self.tile_map == None) or (refresh_cache == True):
            num_tiles = self.get_tile_count()
            tile_width = 8 #TO DO: get these programmatically for each light from the tile info
            tile_height = 8 #TO DO: get these programmatically for each light from the tile info
            (x, y) = self.get_canvas_dimensions()
            #print(x, y)
            tile_map = [[0 for i in range(x)] for j in range(y)]

            tiles = self.get_tile_info()
            x_vals, y_vals = self.get_xy_vals()
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

    def get_tile_effect(self):
        response = self.req_with_resp(GetTileEffect, StateTileEffect)
        effect = {"instanceid": response.instanceid,
                  "type": response.effect_type,
                  "speed": response.speed,
                  "duration": response.duration,
                  "parameters": response.parameters,
                  "palette": response.palette}
        return effect

    def set_tile_effect(self, effect_type=0, speed=0, duration=0, palette=[], instanceid=0, parameters=[], rapid=False):
        if len(palette)>16:
            raise InvalidParameterException("Maximum palette size is 16, {} given.".format(len(palette)))
        if len(parameters)>8:
            raise InvalidParameterException("Maximum parameters size is 8, {} given.".format(len(parameters)))

        # parameters is not currently used by any effect, so just zero these out for now
        if len(parameters) < 8:
            for i in range(len(parameters), 8):
                parameters.append(0)

        payload = {"reserved1": 0,
                   "reserved2": 0,
                   "instanceid": instanceid,
                   "type": effect_type,
                   "speed": speed,
                   "duration": duration,
                   "reserved3": 0,
                   "reserved4": 0,
                   "parameters": parameters,
                   "palette_count": len(palette),
                   "palette": palette}
        if not rapid:
            self.req_with_ack(SetTileEffect, payload)
        else:
            self.fire_and_forget(SetTileEffect, payload, num_repeats=1)


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
