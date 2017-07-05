import thread
from .lifxlan import LifxLAN

class Group(object):

    def __init__(self, devices=[], verbose=False):
        self.devices = devices
        self.verbose = verbose

    def add_device(self, device_object):
        self.devices.append(device_object)

    # relies on discovery, so will be slow if you haven't run discovery yet
    def add_device_by_name(self, device_name):
       lan = LifxLAN()
       d = lan.get_device_by_name(device_name)
       self.devices.append(d)

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

    def set_power(self, power, duration=0, rapid=False):
        for d in self.devices:
            thread.start_new_thread(self.set_power_helper, (power, duration, rapid))

    def set_power_helper(self, power, duration, rapid):
        try:
            d.set_power(power, duration, rapid) # Light::set_power(power, [duration], [rapid])
        except TypeError:
            d.set_power(power, rapid) # Device::set_power(power, [rapid])

    def set_color(self, color, duration=0, rapid=False):
        for d in self.devices:
            if d.supports_color():
                thread.start_new_thread(d.set_color, (color, duration, rapid))

    def set_hue(self, hue, duration=0, rapid=False):
        for d in self.devices:
            if d.supports_color():
                thread.start_new_thread(d.set_hue, (hue, duration, rapid))

    def set_brightness(self, brightness, duration=0, rapid=False):
        for d in self.devices:
            if d.supports_color():
                thread.start_new_thread(d.set_brightness, (brightness, duration, rapid))

    def set_saturation(self, saturation, duration=0, rapid=False):
        for d in self.devices:
            if d.supports_color():
                thread.start_new_thread(d.set_saturation, (saturation, duration, rapid))

    def set_colortemp(self, kelvin, duration=0, rapid=False):
        for d in self.devices:
            if d.supports_color():
                thread.start_new_thread(d.set_colortemp, (kelvin, duration, rapid))

    def set_infrared(self, infrared_brightness):
        for d in self.devices:
            if d.supports_infrared():
                thread.start_new_thread(d.set_infrared, (infrared_brightness))

    def set_zone_color(self, start, end, color, duration=0, rapid=False, apply=1):
        for d in self.devices:
            if d.supports_multizone():
                thread.start_new_thread(d.set_zone_color, (start, end, color, duration, rapid, apply))

    def set_zone_colors(self, colors, duration=0, rapid=False):
        for d in self.devices:
            if d.supports_multizone():
                thread.start_new_thread(d.set_zone_colors, (colors, duration, rapid, apply))
