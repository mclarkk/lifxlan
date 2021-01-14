# Useful to have, non-LAN functions
# Rev 0.1
# Date 06/08/2017
# Author: BHCunningham
#
# 1) RGB to HSBK conversion function
#

### Convert an RGB colour definition to HSBK
# Author : BHCunningham
# Input: (Red, Green, Blue), Temperature
# Colours = 0 -> 255
# Temperature 2500-9000 K, 3500 is default.
# Output: (Hue, Saturation, Brightness, Temperature)

def RGBtoHSBK (RGB, temperature = 3500):
    cmax = max(RGB)
    cmin = min(RGB)
    cdel = cmax - cmin

    brightness = int((cmax/255) * 65535)

    if cdel != 0:
        saturation = int(((cdel) / cmax) * 65535)

        redc = (cmax - RGB[0]) / (cdel)
        greenc = (cmax - RGB[1]) / (cdel)
        bluec = (cmax - RGB[2]) / (cdel)

        if RGB[0] == cmax:
            hue = bluec - greenc
        else:
            if RGB[1] == cmax:
                hue = 2 + redc - bluec
            else:
                hue = 4 + greenc - redc

        hue = hue / 6
        if hue < 0:
            hue = hue + 1

        hue = int(hue*65535)
    else:
        saturation = 0
        hue = 0

    return (hue, saturation, brightness, temperature)
