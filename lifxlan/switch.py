# coding=utf-8
# switch.py
# Author: David Kit

import random
from .device import Device
from .errors import InvalidParameterException, WorkflowException
from .msgtypes import SetRPower, GetRPower, StateRPower

class Switch(Device):
    def __init__(self, mac_addr, ip_addr, service=1, port=56700, source_id=random.randrange(2, 1 << 32), verbose=False):
        mac_addr = mac_addr.lower()
        super(Switch, self).__init__(mac_addr, ip_addr, service, port, source_id, verbose)
        
    ############################################################################
    #                                                                          #
    #                            Switch API Methods                            #
    #                                                                          #
    ############################################################################

    # GetRPower - power level
    def get_relay_power(self, relay_index):
        try:
            response = self.req_with_resp(GetRPower, StateRPower)
            self.level = response.level
        except WorkflowException as e:
            raise
        return self.level

    def set_relay_power(self, relay_index, power):
        on = [True, 1, "on", 65535]
        off = [False, 0, "off"]
        try:
            if power in on:
                self.req_with_ack(SetRPower, {"relay_index": relay_index, "level": 65535})
            elif power in off:
                self.req_with_ack(SetRPower, {"relay_index": relay_index, "level": 0})
            else:
                raise
        except WorkflowException as e:
            raise

    ############################################################################
    #                                                                          #
    #                            String Formatting                             #
    #                                                                          #
    ############################################################################

    def __str__(self):
        self.refresh()
        s = "Switch Relay"
        return s
