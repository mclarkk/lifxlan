#!/usr/bin/env python

from lifxlan import *

lifxlan = LifxLAN()

lifxlan.set_power_all_lights("off", rapid=True)
