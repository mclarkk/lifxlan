# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 19:55:42 2020

@author: Dell
"""
import ifaddr
from lifxlan import LifxLAN, group, device, light
foco2=light.Light("D0:73:D5:5E:25:BD","192.168.0.3")
foco1=light.Light("D0:73:D5:5C:A7:DB","192.168.0.9")
foco = LifxLAN()
#foco.set_power_all_lights("on", rapid = False)
def brillo():
    valor = int(input("Ingresa el valor: "))
    cual = int(input("que foco quieres modificar: "))
    if cual==1:   
        foco1.set_brightness(valor)
        brillo()
    elif cual==2: 
        foco2.set_brightness(valor)
        brillo()
brillo()

