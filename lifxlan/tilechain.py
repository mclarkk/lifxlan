import os
from typing import Optional

from .light import Light
from .msgtypes import GetTileState64, StateTileState64, SetTileState64, GetDeviceChain, StateDeviceChain, \
    SetUserPosition
from .utils import exhaust, init_log, WaitPool

log = init_log(__name__)


class TileChain(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        super(TileChain, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)
        self._wait_pool = WaitPool(5)
        self.tile_info = None
        self.tile_count = None
        self.tile_map = None
        self.canvas_dimensions = None
        self.get_tile_info()
        self._get_tile_map()
        self._get_canvas_dimensions()

    def get_tile_info(self, refresh_cache=False):
        """set tile info and count"""
        if self.tile_info is None or refresh_cache:
            response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
            self.tile_info = [Tile.from_response(t) for t, _ in zip(response.tile_devices, range(response.total_count))]
            self.tile_count = response.total_count
        return self.tile_info

    def get_tile_count(self, refresh_cache=False):
        """set tile count"""
        if self.tile_count is None or refresh_cache:
            response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
            self.tile_count = response.total_count
        return self.tile_count

    def _validate_tile_access(self, tile_idx):
        """ensure valid tile index"""
        if (tile_idx < 0) or (tile_idx >= self.tile_count):
            raise ValueError(f'{tile_idx} is not a valid tile_idx for TileChain with {self.tile_count} tiles.')

    def _get_tile_range(self, tile_idx, num_tiles) -> range:
        end_tile_idx = min((num_tiles or self.tile_count) + tile_idx + 1, self.tile_count)
        return range(tile_idx, end_tile_idx)

    def get_tile_colors(self, tile_idx, x=0, y=0, width=8):
        """get colors for individual tile"""
        self._validate_tile_access(tile_idx)
        payload = dict(tile_index=tile_idx, length=1, reserved=0, x=x, y=y, width=width)
        return self.req_with_resp(GetTileState64, StateTileState64, payload)

    def get_tilechain_colors(self, start_tile_idx=0, num_tiles: Optional[int] = None):
        """get colors for num_tiles starting from start_tile_idx"""
        with self._wait_pool as wp:
            exhaust(wp.submit(self.get_tile_colors, tile_idx)
                    for tile_idx in self._get_tile_range(start_tile_idx, num_tiles))
        return wp.results

    def set_tile_colors(self, start_index, colors, duration=0, tile_count=1, x=0, y=0, width=8, rapid=False):
        """set colors for individual tile"""
        self._validate_tile_access(start_index)

        payload = dict(tile_index=start_index, length=tile_count, colors=colors, duration=duration, reserved=0, x=x,
                       y=y, width=width)
        return self._send_set_message(SetTileState64, payload, rapid=rapid)

    def set_tilechain_colors(self, idx_colors_map, duration=0, rapid=True):
        """set colors for num_tiles starting from start_tile_idx"""
        with self._wait_pool as wp:
            exhaust(wp.submit(self.set_tile_colors, i, c, duration, 1, 0, 0, 8, rapid)
                    for i, c in idx_colors_map.items())

    # ==================================================================================================================
    # HELPER FUNCTIONS
    # ==================================================================================================================

    # danger zoooooone
    def _set_tile_coordinates(self, tile_index, x, y):
        self.req_with_ack(SetUserPosition, {"tile_index": tile_index, "reserved": 0, "user_x": x, "user_y": y})
        # update cached information
        self.get_tile_info(refresh_cache=True)
        self._get_tile_map(refresh_cache=True)
        self._get_canvas_dimensions(refresh_cache=True)

    def _get_xy_vals(self):
        tiles = self.get_tile_info()
        num_tiles = self.get_tile_count()
        x_vals = []
        y_vals = []
        for tile in tiles[:num_tiles]:
            x_vals.append(tile.user_x)
            y_vals.append(tile.user_y)
        x_vals = self._center_axis(x_vals)
        y_vals = self._center_axis(y_vals)
        return x_vals, y_vals

    @staticmethod
    def _center_axis(axis_vals):
        if 0.0 not in axis_vals:
            smallest_val = min([abs(val) for val in axis_vals])
            closest_val = 0.0
            for val in axis_vals:
                if abs(val) == smallest_val:
                    closest_val = val
            axis_vals = [(-1 * closest_val) + val for val in axis_vals]
        return axis_vals

    # all become non-negative -- shifts (0, 0) to the left/top
    @staticmethod
    def _shift_axis_upper_left(axis_vals, is_y=False):
        if is_y:
            axis_vals = [-1 * val for val in axis_vals]
        smallest_val = min(axis_vals)
        axis_vals = [(-1 * smallest_val) + val for val in axis_vals]
        return axis_vals

    def _get_canvas_dimensions(self, refresh_cache=False):
        if (self.canvas_dimensions is None) or refresh_cache:
            x_vals, y_vals = self._get_xy_vals()
            min_x = min(x_vals)
            max_x = max(x_vals)
            min_y = min(y_vals)
            max_y = max(y_vals)
            x_tilespan = (max_x - min_x) + 1
            y_tilespan = (max_y - min_y) + 1
            tile_width = 8  # TO DO: get these programmatically for each light from the tile info
            tile_height = 8  # TO DO: get these programmatically for each light from the tile info
            canvas_x = int(x_tilespan * tile_width)
            canvas_y = int(y_tilespan * tile_height)
            self.canvas_dimensions = (canvas_x, canvas_y)
        return self.canvas_dimensions

    def _get_tile_map(self, refresh_cache=False):
        if (self.tile_map is None) or refresh_cache:
            num_tiles = self.get_tile_count()
            tile_width = 8  # TO DO: get these programmatically for each light from the tile info
            tile_height = 8  # TO DO: get these programmatically for each light from the tile info
            x, y = self._get_canvas_dimensions()
            tile_map = [[0] * x for _ in range(y)]

            tiles = self.get_tile_info()
            x_vals, y_vals = self._get_xy_vals()
            x_vals = self._shift_axis_upper_left(x_vals)
            y_vals = self._shift_axis_upper_left(y_vals, is_y=True)

            for i in range(num_tiles):
                tile = tiles[i]
                x_start_tilespan = x_vals[i]
                y_start_tilespan = y_vals[i]
                # print(i, x_start_tilespan, y_start_tilespan)
                x_start_pixel = int(x_start_tilespan * tile_width)
                y_start_pixel = int(y_start_tilespan * tile_height)
                for j in range(y_start_pixel, y_start_pixel + tile_width):
                    for k in range(x_start_pixel, x_start_pixel + tile_height):
                        j0 = j - y_start_pixel
                        k0 = k - x_start_pixel
                        tile_map[j][k] = (i, (j0 * tile_width + k0))

            # for row in tile_map:
            #    print(row)
            self.tile_map = tile_map
        return self.tile_map


class Tile(object):
    def __init__(self, accel_meas_x, accel_meas_y, accel_meas_z, user_x, user_y, width=8, height=8,
                 device_version_vendor=None, device_version_product=None, device_version_version=None,
                 firmware_build=None, firmware_version=None):
        super(Tile, self).__init__()
        self.accel_meas_x = accel_meas_x
        self.accel_meas_y = accel_meas_y
        self.accel_meas_z = accel_meas_z
        self.user_x = user_x
        self.user_y = user_y
        self.width = width
        self.height = height
        self.device_version_vendor = device_version_vendor
        self.device_version_product = device_version_product
        self.device_version_version = device_version_version
        self.firmware_build = firmware_build
        self.firmware_version = firmware_version

    @classmethod
    def from_response(cls, resp):
        fields = ('accel_meas_x accel_meas_y accel_meas_z user_x user_y width height device_version_vendor '
                  'device_version_product device_version_version firmware_build firmware_version')
        return cls(*map(resp.get, fields.split()))

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
