import os

from .device import WorkflowException
from .light import Light
from .msgtypes import GetTileState64, StateTileState64, SetTileState64

class TileChain(Light):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=os.getpid(), verbose=False):
        super(TileChain, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)

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
