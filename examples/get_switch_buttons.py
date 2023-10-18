import json

from lifxlan import LifxLAN

lifx = LifxLAN()
switches = lifx.get_switches()


for sw in switches:
    print(sw.get_label())
    _, _, buttons_count, buttons = sw.get_buttons()
    print("\t", json.dumps(buttons, indent=4, default=str).replace("\n", "\n\t"))

    for i in range(4):
        print(
            f"\tRelay {i}: {'Off' if sw.get_relay_power(i) in [False, 0, 'off'] else 'On'}"
        )
