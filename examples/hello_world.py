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
	print("\nFound {} light(s):\n".format(len(devices)))
	for d in devices:
		print(d)

if __name__=="__main__":
	main()