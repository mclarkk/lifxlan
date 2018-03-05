import os

from .device import WorkflowException
from .light import Light
from .msgtypes import GetTileState64, StateTileState64, SetTileState64, GetDeviceChain, StateDeviceChain, SetUserPosition

class TileChain(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        super(TileChain, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)

    def get_chain_state(self):
        response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
        print(response)
        tiles = []
        for tile in response.tile_devices:
            t = Tile(tile["user_x"], tile["user_y"], tile["width"], tile["height"], tile["device_version_vendor"], tile["device_version_product"], tile["device_version_version"], tile["firmware_build"], tile["firmware_version"])
            tiles.append(t)
        return tiles

    def get_total_tile_count(self):
        response = self.req_with_resp(GetDeviceChain, StateDeviceChain)
        self.total_count = response.total_count
        return self.total_count

    def set_user_position(self):
        pass

    def get_tile_colors(self, start_index, tile_count=1, x=0, y=0, width=8):
        # ADD VALIDATION HERE

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
        s = "Tile Info:"
        s += "\nUser X: " + str(self.user_x)
        s += "\nUser Y: " + str(self.user_y)
        s += "\nWidth: " + str(self.width)
        s += "\nHeight: " + str(self.height)
        s += "\nDevice Version Vendor: " + str(self.device_version_vendor)
        s += "\nDevice Version Product: " + str(self.device_version_product)
        s += "\nDevice Version Version: " + str(self.device_version_version)
        s += "\nFirmware Build: " + str(self.firmware_build)
        s += "\nFirmware Version: " + str(self.firmware_version)
        return s
