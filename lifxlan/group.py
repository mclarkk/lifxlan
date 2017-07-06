#import thread
from threading import Thread
from time import sleep
import sys

class Group(object):

    def __init__(self, devices=[], verbose=False):
        self.devices = devices
        self.verbose = verbose

    def add_device(self, device_object):
        self.devices.append(device_object)

    def remove_device(self, device_object):
        new_devices = []
        for d in self.devices:
            if d != device_object:
                new_devices.append(d)
        self.devices = new_devices

    def remove_device_by_name(self, device_name):
        new_devices = []
        for d in self.devices:
            if d.get_name() != device_name:
                new_devices.append(d)
        self.devices = new_devices

    def get_device_list(self):
        return self.devices

    def set_power(self, power, duration=0, rapid=False):
        threads = []
        for d in self.devices:
            t = Thread(target = self.set_power_helper, args = (d, power, duration, rapid))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def set_power_helper(self, device, power, duration, rapid):
        if device.is_light():
            device.set_power(power, duration, rapid) # Light::set_power(power, [duration], [rapid])
        else:
            device.set_power(power, rapid) # Device::set_power(power, [rapid])

    def set_color(self, color, duration=0, rapid=False):
        # pre-calculate which devices you'll operate on
        # it'll make the color change look more simultaneous
        color_supporting_devices = []
        for d in self.devices:
            if d.supports_color:
                color_supporting_devices.append(d)
        # multi-threaded color change
        threads = []
        for d in color_supporting_devices:
            t = Thread(target = d.set_color, args = (color, duration, rapid))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    # Hue, saturation, brightness, and colortemp are a little different than the
    # other functions. You can't just spawn a new thread with "set_saturation"
    # or whatever for each device, because each command will first request the
    # current color from the bulbs, which will take different amounts of time to
    # receive, which makes the color change take different amounts for each
    # bulb. So basically you gotta get all the colors up front and then make
    # a set_color() call for each bulb.

    def set_hue(self, hue, duration=0, rapid=False):
        # pre-calculate which devices to operate on
        color_supporting_devices = []
        for d in self.devices:
            if d.supports_color:
                color_supporting_devices.append(d)
        # get colors
        colors = []
        for d in color_supporting_devices:
            colors.append(d.get_color())
        # "simultaneous" change
        threads = []
        for (i, d) in enumerate(color_supporting_devices):
            _, saturation, brightness, kelvin = colors[i]
            color = [hue, saturation, brightness, kelvin]
            t = Thread(target = d.set_color, args = (color, duration, rapid))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def set_brightness(self, brightness, duration=0, rapid=False):
        # pre-calculate which devices to operate on
        color_supporting_devices = []
        for d in self.devices:
            if d.supports_color:
                color_supporting_devices.append(d)
        # get colors
        colors = []
        for d in color_supporting_devices:
            colors.append(d.get_color())
        # "simultaneous" change
        threads = []
        for (i, d) in enumerate(color_supporting_devices):
            hue, saturation, _, kelvin = colors[i]
            color = [hue, saturation, brightness, kelvin]
            t = Thread(target = d.set_color, args = (color, duration, rapid))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def set_saturation(self, saturation, duration=0, rapid=False):
        # pre-calculate which devices to operate on
        color_supporting_devices = []
        for d in self.devices:
            if d.supports_color:
                color_supporting_devices.append(d)
        # get colors
        colors = []
        for d in color_supporting_devices:
            colors.append(d.get_color())
        # "simultaneous" change
        threads = []
        for (i, d) in enumerate(color_supporting_devices):
            hue, _, brightness, kelvin = colors[i]
            color = [hue, saturation, brightness, kelvin]
            t = Thread(target = d.set_color, args = (color, duration, rapid))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def set_colortemp(self, kelvin, duration=0, rapid=False):
        # pre-calculate which devices to operate on
        color_supporting_devices = []
        for d in self.devices:
            if d.supports_color:
                color_supporting_devices.append(d)
        # get colors
        colors = []
        for d in color_supporting_devices:
            colors.append(d.get_color())
        # "simultaneous" change
        threads = []
        for (i, d) in enumerate(color_supporting_devices):
            hue, saturation, brightness, _ = colors[i]
            color = [hue, saturation, brightness, kelvin]
            t = Thread(target = d.set_color, args = (color, duration, rapid))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def set_infrared(self, infrared_brightness):
        # pre-calculate which devices to operate on
        infrared_supporting_devices = []
        for d in self.devices:
            if d.supports_infrared():
                infrared_supporting_devices.append(d)
        # "simultaneous" change
        threads = []
        for d in infrared_supporting_devices:
            t = Thread(target = d.set_infrared, args = (infrared_brightness))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def set_zone_color(self, start, end, color, duration=0, rapid=False, apply=1):
        # pre-calculate which devices to operate on
        multizone_devices = []
        for d in self.devices:
            if d.supports_multizone():
                multizone_devices.append(d)
        # "simultaneous" change
        threads = []
        for d in multizone_devices:
            t = Thread(target = d.set_zone_color, args = (start, end, color, duration, rapid, apply))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def set_zone_colors(self, colors, duration=0, rapid=False):
        # pre-calculate which devices to operate on
        multizone_devices = []
        for d in self.devices:
            if d.supports_multizone():
                multizone_devices.append(d)
        # "simultaneous" change
        threads = []
        for d in multizone_devices:
            t = Thread(target = d.set_zone_colors, args = (colors, duration, rapid, apply))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def __str__(self):
        s = "Group ({}):\n\n".format(len(self.devices))
        for d in self.devices:
            s += str(d) + "\n"
        return s
