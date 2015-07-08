from lifxlan import *
import sys

def main():
    num_lights = None
    if len(sys.argv) != 2:
        print("\nDiscovery will go much faster if you provide the number of lights on your LAN:")
        print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
    else:
        num_lights = int(sys.argv[1])

    # instantiate LifxLAN client
    print("Discovering lights...")
    lifx = LifxLAN(num_lights)

    # get devices
    devices = lifx.get_lights()
    bulb = devices[0]
    print("Selected {}".format(bulb.get_label()))

    # get color
    original_color = bulb.get_color()

    print("Toggling power...")
    toggle_device_power(bulb, 0.2)

    print("Toggling color...")
    toggle_light_color(bulb, 0.2)

    # restore original color
    bulb.set_color(original_color)

def toggle_device_power(device, interval=0.5, num_cycles=3): #TEST
    original_power_state = device.get_power()
    device.set_power("off")
    rapid = True if interval < 1 else False
    for i in range(num_cycles):
        device.set_power("on", rapid)
        sleep(interval)
        device.set_power("off", rapid)
        sleep(interval)
    device.set_power(original_power_state)

def toggle_light_color(light, interval=0.5, num_cycles=3):
    original_color = light.get_color()
    rapid = True if interval < 1 else False
    for i in range(num_cycles):
        light.set_color(BLUE, rapid=rapid)
        sleep(interval)
        light.set_color(GREEN, rapid=rapid)
        sleep(interval)
    light.set_color(original_color)

if __name__=="__main__":
    main()