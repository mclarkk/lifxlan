# msgtypes.py
# Author: Meghan Clark

# To Do: Validate that args are within required ranges, types, etc. In particular: Color [0-65535, 0-65535, 0-65535, 2500-9000], Power Level (must be 0 OR 65535)
# Need to look into assert-type frameworks or something, there has to be a tool for that.
# Also need to make custom errors possibly, though tool may have those.

from message import Message, BROADCAST_MAC, HEADER_SIZE_BYTES, little_endian
import bitstring
import sys
import struct

##### DEVICE MESSAGES #####

class GetService(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        target_addr = BROADCAST_MAC
        super(GetService, self).__init__(MSG_IDS[GetService], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateService(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.service = payload["service"] 
        self.port = payload["port"]
        super(StateService, self).__init__(MSG_IDS[StateService], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Service", self.service))
        self.payload_fields.append(("Port", self.port))
        service = little_endian(bitstring.pack("8", self.service))
        port = little_endian(bitstring.pack("32", self.port))
        payload = service + port
        return payload


class GetHostInfo(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetHostInfo, self).__init__(MSG_IDS[GetHostInfo], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateHostInfo(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.signal = payload["signal"]
        self.tx = payload["tx"]
        self.rx = payload["rx"]
        self.reserved1 = payload["reserved1"]
        super(StateHostInfo, self).__init__(MSG_IDS[StateHostInfo], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Signal (mW)", self.signal))
        self.payload_fields.append(("TX (bytes since on)", self.tx))
        self.payload_fields.append(("RX (bytes since on)", self.rx))
        self.payload_fields.append(("Reserved", self.reserved1))
        signal = little_endian(bitstring.pack("32", self.signal))
        tx = little_endian(bitstring.pack("32", self.tx))
        rx = little_endian(bitstring.pack("32", self.rx))
        reserved1 = little_endian(bitstring.pack("16", self.reserved1))
        payload = signal + tx + rx + reserved1
        return payload


class GetHostFirmware(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetHostFirmware, self).__init__(MSG_IDS[GetHostFirmware], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateHostFirmware(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.build = payload["build"] 
        self.reserved1 = payload["reserved1"]
        self.version = payload["version"]
        super(StateHostFirmware, self).__init__(MSG_IDS[StateHostFirmware], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Timestamp of Build", self.build))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Version", self.version))
        build = little_endian(bitstring.pack("64", self.build))
        reserved1 = little_endian(bitstring.pack("64", self.reserved1))
        version = little_endian(bitstring.pack("32", self.version))
        payload = build + reserved1 + version
        return payload


class GetWifiInfo(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetWifiInfo, self).__init__(MSG_IDS[GetWifiInfo], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateWifiInfo(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.signal = payload["signal"] 
        self.tx = payload["tx"]
        self.rx = payload["rx"]
        self.reserved1 = payload["reserved1"]
        super(StateWifiInfo, self).__init__(MSG_IDS[StateWifiInfo], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Signal (mW)", self.signal))
        self.payload_fields.append(("TX (bytes since on)", self.tx))
        self.payload_fields.append(("RX (bytes since on)", self.rx))
        self.payload_fields.append(("Reserved", self.reserved1))
        signal = little_endian(bitstring.pack("32", self.signal))
        tx = little_endian(bitstring.pack("32", self.tx))
        rx = little_endian(bitstring.pack("32", self.rx))
        reserved1 = little_endian(bitstring.pack("16", self.reserved1))
        payload = signal + tx + rx + reserved1
        return payload


class GetWifiFirmware(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetWifiFirmware, self).__init__(MSG_IDS[GetWifiFirmware], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateWifiFirmware(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.build = payload["build"] 
        self.reserved1 = payload["reserved1"]
        self.version = payload["version"]
        super(StateWifiFirmware, self).__init__(MSG_IDS[StateWifiFirmware], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Timestamp of Build", self.build))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Version", self.version))
        build = little_endian(bitstring.pack("64", self.build))
        reserved1 = little_endian(bitstring.pack("64", self.reserved1))
        version = little_endian(bitstring.pack("32", self.version))
        payload = build + reserved1 + version
        return payload


class GetPower(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetPower, self).__init__(MSG_IDS[GetPower], target_addr, source_id, seq_num, ack_requested, response_requested)


class SetPower(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.power_level = payload["power_level"]
        super(SetPower, self).__init__(MSG_IDS[SetPower], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Power", self.power_level))
        power_level = little_endian(bitstring.pack("16", self.power_level))
        payload = power_level
        return payload


class StatePower(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.power_level = payload["power_level"]
        super(StatePower, self).__init__(MSG_IDS[StatePower], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Power", self.power_level))
        power_level = little_endian(bitstring.pack("16", self.power_level))
        payload = power_level
        return payload


class GetLabel(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetLabel, self).__init__(MSG_IDS[GetLabel], target_addr, source_id, seq_num, ack_requested, response_requested)


class SetLabel(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.label = payload["label"]
        super(SetLabel, self).__init__(MSG_IDS[SetLabel], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Label", self.label))
        field_len_bytes = 32
        label = "".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label)
        padding = "".join(little_endian(bitstring.pack("8", 0)) for i in range(field_len_bytes-len(self.label)))
        payload = label + padding
        return payload


class StateLabel(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.label = payload["label"]
        super(StateLabel, self).__init__(MSG_IDS[StateLabel], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Label", self.label))
        field_len_bytes = 32
        label = "".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label)
        padding = "".join(little_endian(bitstring.pack("8", 0)) for i in range(field_len_bytes-len(self.label)))
        payload = label + padding
        return payload


class GetVersion(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetVersion, self).__init__(MSG_IDS[GetVersion], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateVersion(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.vendor = payload["vendor"] 
        self.product = payload["product"]
        self.version = payload["version"]
        super(StateVersion, self).__init__(MSG_IDS[StateVersion], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Vendor", self.vendor))
        self.payload_fields.append(("Reserved", self.product))
        self.payload_fields.append(("Version", self.version))
        vendor = little_endian(bitstring.pack("32", self.vendor))
        product = little_endian(bitstring.pack("32", self.product))
        version = little_endian(bitstring.pack("32", self.version))
        payload = vendor + product + version
        return payload


class GetInfo(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetInfo, self).__init__(MSG_IDS[GetInfo], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateInfo(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.time = payload["time"] 
        self.uptime = payload["uptime"]
        self.downtime = payload["downtime"]
        super(StateInfo, self).__init__(MSG_IDS[StateInfo], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Current Time", self.time))
        self.payload_fields.append(("Uptime (ns)", self.uptime))
        self.payload_fields.append(("Last Downtime Duration (ns) (5 second error)", self.downtime))
        time = little_endian(bitstring.pack("64", self.time))
        uptime = little_endian(bitstring.pack("64", self.uptime))
        downtime = little_endian(bitstring.pack("64", self.downtime))
        payload = time + uptime + downtime
        return payload


class Acknowledgement(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(Acknowledgement, self).__init__(MSG_IDS[Acknowledgement], target_addr, source_id, seq_num, ack_requested, response_requested)


class EchoRequest(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.byte_array = payload["byte_array"]
        super(EchoRequest, self).__init__(MSG_IDS[EchoRequest], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        field_len = 64
        self.payload_fields.append(("Byte Array", self.byte_array))
        byte_array = "".join(little_endian(bitstring.pack("8", b)) for b in self.byte_array)
        byte_array_len = len(byte_array)
        if byte_array_len < field_len:
            byte_array += "".join(little_endian(bitstring.pack("8", 0)) for i in range(field_len-byte_array_len))
        elif byte_array_len > field_len:
            byte_array = byte_array[:field_len]
        payload = byte_array
        return payload


class EchoResponse(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.byte_array = payload["byte_array"]
        super(EchoResponse, self).__init__(MSG_IDS[EchoResponse], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Byte Array", self.byte_array))
        byte_array = "".join(little_endian(bitstring.pack("8", b)) for b in self.byte_array)
        payload = byte_array
        return payload


##### LIGHT MESSAGES #####


class LightGet(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(LightGet, self).__init__(MSG_IDS[LightGet], target_addr, source_id, seq_num, ack_requested, response_requested)


class LightSetColor(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.color = payload["color"]
        self.duration = payload["duration"]
        super(LightSetColor, self).__init__(MSG_IDS[LightSetColor], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        reserved_8 = little_endian(bitstring.pack("8", self.reserved))
        color = "".join(little_endian(bitstring.pack("16", field)) for field in self.color)
        duration = little_endian(bitstring.pack("32", self.duration))
        payload = reserved_8 + color + duration
        return payload


class LightState(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.color = payload["color"]
        self.reserved1 = payload["reserved1"]
        self.power_level = payload["power_level"]
        self.label = payload["label"]
        self.reserved2 = payload["reserved2"]
        super(LightState, self).__init__(MSG_IDS[LightState], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Color (HSBK)", self.color))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Power Level", self.power_level))
        self.payload_fields.append(("Label", self.label))
        self.payload_fields.append(("Reserved", self.reserved2))
        color = "".join(little_endian(bitstring.pack("16", field)) for field in self.color)
        reserved1 = little_endian(bitstring.pack("16", self.reserved1))
        power_level = little_endian(bitstring.pack("16", self.power_level))
        label = "".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label)
        label_padding = "".join(little_endian(bitstring.pack("8", 0)) for i in range(32-len(self.label)))
        label += label_padding
        reserved2 = little_endian(bitstring.pack("64", self.reserved1))
        payload = color + reserved1 + power_level + label + reserved2
        return payload


class LightGetPower(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(LightGetPower, self).__init__(MSG_IDS[LightGetPower], target_addr, source_id, seq_num, ack_requested, response_requested)


class LightSetPower(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.power_level = payload["power_level"]
        self.duration = payload["duration"]
        super(LightSetPower, self).__init__(MSG_IDS[LightSetPower], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        power_level = little_endian(bitstring.pack("16", self.power_level))
        duration = little_endian(bitstring.pack("32", self.duration))
        payload = power_level + duration
        return payload


class LightStatePower(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.power_level = payload["power_level"]
        super(LightStatePower, self).__init__(MSG_IDS[LightStatePower], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Power Level", self.power_level))
        power_level = little_endian(bitstring.pack("16", self.power_level))
        payload = power_level
        return payload


MSG_IDS = {     GetService: 2, 
                StateService: 3, 
                GetHostInfo: 12, 
                StateHostInfo: 13, 
                GetHostFirmware: 14, 
                StateHostFirmware: 15, 
                GetWifiInfo: 16, 
                StateWifiInfo: 17, 
                GetWifiFirmware: 18, 
                StateWifiFirmware: 19, 
                GetPower: 20, 
                SetPower: 21, 
                StatePower: 22, 
                GetLabel: 23, 
                SetLabel: 24, 
                StateLabel: 25, 
                GetVersion: 32, 
                StateVersion: 33, 
                GetInfo: 34, 
                StateInfo: 35, 
                Acknowledgement: 45, 
                EchoRequest: 58, 
                EchoResponse: 59,
                LightGet: 101,
                LightSetColor: 102,
                LightState: 107,
                LightGetPower: 116,
                LightSetPower: 117,
                LightStatePower: 118}

SERVICE_IDS = { 1: "UDP",
                2: "reserved",
                3: "reserved",
                4: "reserved"}

STR_MAP = { 65535: "On",
            0: "Off",
            None: "Unknown"}

def str_map(key):
    string_representation = "Unknown"
    if key == None:
        string_representation = "Unknown"
    elif type(key) == type(0):
        if key > 0 and key <= 65535:
            string_representation = "On"
        elif key == 0:
            string_representation = "Off" 
    return string_representation
