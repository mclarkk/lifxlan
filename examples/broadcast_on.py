#!/usr/bin/env python3

from lifxlan import *

lifxlan = LifxLAN()

lifxlan.set_power_all_lights('on', rapid=True)
