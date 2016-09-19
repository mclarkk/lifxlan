#!/usr/bin/env python

from __future__ import unicode_literals
from lifxlan import *

lifxlan = LifxLAN()

lifxlan.set_power_all_lights("on", rapid=True)
