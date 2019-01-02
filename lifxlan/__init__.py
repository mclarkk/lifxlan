# from .lifxlan import LifxLAN
from .group import Group, LifxLAN
from .message import *
from .msgtypes import *
from .unpack import unpack_lifx_message
from .device import *
from .light import *
from .multizonelight import *
from .tilechain import TileChain, Tile
from .utils import *
from .themes import Theme, Themes
from .colors import Color, Colors
from .grid import grid, GridLight, Dir

__version__     = '2.0.0'
__description__ = 'API for local communication with LIFX devices over a LAN.'
__url__         = 'http://github.com/sweettuse/lifxlan'
__author__      = 'Meghan Clark, adam cushner'
__authoremail__ = 'mclarkk@berkeley.edu; adam.cushner@gmail.com'
__license__     = 'MIT'
