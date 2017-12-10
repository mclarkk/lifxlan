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

def RGBtoHSBK (RGB, Temperature = 3500):
    cmax = max(RGB)
    cmin = min(RGB)
    cdel = cmax - cmin
    
    Brightness = int((cmax/255) * 65535)

    if cdel != 0:
        Saturation = int(((cdel) / cmax) * 65535)

        redc = (cmax - RGB[0]) / (cdel)
        greenc = (cmax - RGB[1]) / (cdel)
        bluec = (cmax - RGB[2]) / (cdel)
        
        if RGB[0] == cmax:
            Hue = bluec - greenc
        else:
            if RGB[1] == cmax:
                Hue = 2 + redc - bluec    
            else:
                Hue = 4 + greenc - redc
                
        Hue = Hue / 6
        if Hue < 0:
            Hue = Hue + 1 
            
        Hue = int(Hue*65535)        
    else:
        Saturation = 0
        Hue = 0
    
    return (Hue, Saturation, Brightness, Temperature)
