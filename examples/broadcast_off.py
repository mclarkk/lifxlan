#!/usr/bin/env python
# coding=utf-8

from lifxlan import LifxLAN

lifxlan = LifxLAN()

lifxlan.set_power_all_lights("off", rapid=True)
