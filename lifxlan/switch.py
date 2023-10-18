# coding=utf-8
# switch.py
# Author: David Kit

import random

from .device import Device
from .errors import WorkflowException
from .msgtypes import ButtonGet, ButtonState, GetRPower, SetRPower, StateRPower


class Switch(Device):
    def __init__(
        self,
        mac_addr,
        ip_addr,
        service=1,
        port=56700,
        source_id=random.randrange(2, 1 << 32),
        verbose=True,
    ):
        mac_addr = mac_addr.lower()
        super(Switch, self).__init__(
            mac_addr, ip_addr, service, port, source_id, verbose
        )
        self.buttons_count = 0
        self.buttons = []

    ############################################################################
    #                                                                          #
    #                            Switch API Methods                            #
    #                                                                          #
    ############################################################################

    # GetRPower - power level
    def get_relay_power(self, relay_index):
        try:
            response = self.req_with_resp(
                GetRPower, StateRPower, {"relay_index": relay_index}
            )
            self.level = response.level
        except WorkflowException:
            raise
        return self.level

    def set_relay_power(self, relay_index, level):
        on = [True, 1, "on", 65535, "True", "65535"]
        off = [False, 0, "off", "False", "0"]
        assert level in on or level in off
        try:
            if level in on:
                self.req_with_ack(
                    SetRPower, {"relay_index": relay_index, "level": 65535}
                )
            else:
                self.req_with_ack(SetRPower, {"relay_index": relay_index, "level": 0})

        except WorkflowException:
            raise

    def get_buttons(self):
        try:
            response = self.req_with_resp(ButtonGet, ButtonState)
            count = response.count
            index = response.index
            self.buttons_count = response.count
            self.buttons = []
            for button_index in range(self.buttons_count):
                button_result = {"button_index": button_index}
                b = response.buttons[button_index]
                actions_count = b["actions_count"]
                if actions_count > 0:
                    button_result["actions"] = []
                for a in b["actions"][0:actions_count]:
                    match a["gesture"]:
                        case 1:
                            gesture = "Press"
                        case 2:
                            gesture = "Hold"
                        case 3:
                            gesture = "Press twice"
                        case 4:
                            gesture = "Press then hold"
                        case 5:
                            gesture = "Hold twice"
                        case _:
                            continue

                    def _to_hex(l: list[int]) -> str:
                        return "0x" + "".join([f"{i:02x}" for i in l])

                    match a["target_type"]:
                        case 2:
                            target_type = "Relays"
                            relays_count = a["target"]["relays_count"]
                            relays = a["target"]["relays"][0:relays_count]
                            action = {
                                "gesture": gesture,
                                "target_type": target_type,
                                "relays": relays,
                            }
                        case 3:
                            target_type = "Device"
                            serial = a["target"]["serial"]
                            action = {
                                "gesture": gesture,
                                "target_type": target_type,
                                "serial": _to_hex(serial),
                            }
                        case 4:
                            target_type = "Location"
                            location = a["target"]
                            action = {
                                "gesture": gesture,
                                "target_type": target_type,
                                "location": _to_hex(location),
                            }
                        case 5:
                            target_type = "Group"
                            group = a["target"]
                            action = {
                                "gesture": gesture,
                                "target_type": target_type,
                                "group": _to_hex(group),
                            }
                        case 6:
                            target_type = "Scene"
                            scene = a["target"]
                            action = {
                                "gesture": gesture,
                                "target_type": target_type,
                                "scene": _to_hex(scene),
                            }
                        case 7:
                            target_type = "Device Relays"
                            serial = a["target"]["serial"]
                            relays_count = a["target"]["relays_count"]
                            relays = a["target"]["relays"][0:relays_count]
                            action = {
                                "gesture": gesture,
                                "target_type": target_type,
                                "serial": _to_hex(serial),
                                "relays": relays,
                            }
                        case _:
                            continue

                    button_result["actions"].append(action)
                self.buttons.append(button_result)
        except WorkflowException:
            raise
        return count, index, self.buttons_count, self.buttons

    ############################################################################
    #                                                                          #
    #                            String Formatting                             #
    #                                                                          #
    ############################################################################

    def __str__(self):
        self.refresh()
        s = "Switch Relay"
        return s
