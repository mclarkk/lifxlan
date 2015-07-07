import lifxlan
from time import sleep

def main():
	# Toggle power to some device, if present
	devices = lifxlan.get_devices()
	if len(devices) > 0:
		toggle_device_power(devices[0], 3)
		print("Done blinking!")
	else:
		print("No devices found.")

	# Toggle color of some light, if present
	lights = lifxlan.get_lights()
	if len(lights) > 0:
		toggle_light_color(lights[0], 3)
		print("Done")

def toggle_device_power(device, cycles):
	original_power_state = device.get_power()
	for i in range(cycles):
		device.set_power(0)
		sleep(0.5)
		device.set_power(1)
		sleep(0.5)
	device.set_power(original_power_state)

def toggle_light_color(light, cycles):
	original_color = light.get_color()
	for i in range(cycles):
		light.set_color(light.BLUE)
		sleep(0.5)
		light.set_color(light.GREEN)
		sleep(0.5)
	light.set_color(original_color)

if __name__=="__main__":
	main()