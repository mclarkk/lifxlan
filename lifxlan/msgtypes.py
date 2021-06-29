# coding=utf-8
# msgtypes.py
# Author: Meghan Clark

# To Do: Validate that args are within required ranges, types, etc. In particular: Color [0-65535, 0-65535, 0-65535, 2500-9000], Power Level (must be 0 OR 65535)
# Need to look into assert-type frameworks or something, there has to be a tool for that.
# Also need to make custom errors possibly, though tool may have those.

import bitstring

from .message import BROADCAST_MAC, Message, little_endian


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
        try:
            label = b"".join(little_endian(bitstring.pack("8", c)) for c in self.label.encode('utf-8'))
        except ValueError: # because of differences in Python 2 and 3
            label = b"".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label.encode('utf-8'))
        padding = b"".join(little_endian(bitstring.pack("8", 0)) for i in range(field_len_bytes-len(self.label)))
        payload = label + padding
        return payload


class StateLabel(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.label = payload["label"]
        super(StateLabel, self).__init__(MSG_IDS[StateLabel], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Label", self.label))
        field_len_bytes = 32
        try:
            label = b"".join(little_endian(bitstring.pack("8", c)) for c in self.label.encode('utf-8'))
        except ValueError: # because of differences in Python 2 and 3
            label = b"".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label.encode('utf-8'))
        padding = b"".join(little_endian(bitstring.pack("8", 0)) for i in range(field_len_bytes-len(self.label)))
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

class GetLocation(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetLocation, self).__init__(MSG_IDS[GetLocation], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateLocation(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.location = payload["location"]
        self.label = payload["label"]
        self.updated_at = payload["updated_at"]
        super(StateLocation, self).__init__(MSG_IDS[StateLocation], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Location", self.location))
        self.payload_fields.append(("Label", self.label))
        self.payload_fields.append(("Updated At", self.updated_at))
        location = b"".join(little_endian(bitstring.pack("8", b)) for b in self.location)
        try:
            label = b"".join(little_endian(bitstring.pack("8", c)) for c in self.label.encode('utf-8'))
        except ValueError: # because of differences in Python 2 and 3
            label = b"".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label.encode('utf-8'))
        label_padding = b"".join(little_endian(bitstring.pack("8", 0)) for i in range(32-len(self.label)))
        label += label_padding
        updated_at = little_endian(bitstring.pack("64", self.updated_at))
        payload = location + label + updated_at
        return payload

class GetGroup(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetGroup, self).__init__(MSG_IDS[GetGroup], target_addr, source_id, seq_num, ack_requested, response_requested)


class StateGroup(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.group = payload["group"]
        self.label = payload["label"]
        self.updated_at = payload["updated_at"]
        super(StateGroup, self).__init__(MSG_IDS[StateGroup], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Group", self.group))
        self.payload_fields.append(("Label", self.label))
        self.payload_fields.append(("Updated At", self.updated_at))
        group = b"".join(little_endian(bitstring.pack("8", b)) for b in self.group)
        try:
            label = b"".join(little_endian(bitstring.pack("8", c)) for c in self.label.encode('utf-8'))
        except ValueError: # because of differences in Python 2 and 3
            label = b"".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label.encode('utf-8'))
        label_padding = b"".join(little_endian(bitstring.pack("8", 0)) for i in range(32-len(self.label)))
        label += label_padding
        updated_at = little_endian(bitstring.pack("64", self.updated_at))
        payload = group + label + updated_at
        return payload

class Acknowledgement(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(Acknowledgement, self).__init__(MSG_IDS[Acknowledgement], target_addr, source_id, seq_num, ack_requested, response_requested)


class EchoRequest(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.byte_array = payload["byte_array"]
        super(EchoRequest, self).__init__(MSG_IDS[EchoRequest], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Byte Array", self.byte_array))
        field_len = 64
        byte_array = b"".join(little_endian(bitstring.pack("8", b)) for b in self.byte_array)
        byte_array_len = len(byte_array)
        if byte_array_len < field_len:
            byte_array += b"".join(little_endian(bitstring.pack("8", 0)) for i in range(field_len-byte_array_len))
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
        byte_array = b"".join(little_endian(bitstring.pack("8", b)) for b in self.byte_array)
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
        self.payload_fields.append(("Color", self.color))
        self.payload_fields.append(("Duration", self.duration))
        reserved_8 = little_endian(bitstring.pack("8", self.reserved))
        color = b"".join(little_endian(bitstring.pack("16", field)) for field in self.color)
        duration = little_endian(bitstring.pack("32", self.duration))
        payload = reserved_8 + color + duration
        return payload


class LightSetWaveform(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.transient = payload["transient"]
        self.color = payload["color"]
        self.period = payload["period"]
        self.cycles = payload["cycles"]
        self.duty_cycle = payload["duty_cycle"]
        self.waveform = payload["waveform"]
        super(LightSetWaveform, self).__init__(MSG_IDS[LightSetWaveform], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Is Transient", self.transient))
        self.payload_fields.append(("Color", self.color))
        self.payload_fields.append(("Period", self.period))
        self.payload_fields.append(("Cycles", self.cycles))
        self.payload_fields.append(("Duty Cycle", self.duty_cycle))
        self.payload_fields.append(("Waveform", self.waveform))
        reserved_8 = little_endian(bitstring.pack("8", self.reserved))
        transient = little_endian(bitstring.pack("uint:8", self.transient))
        color = b"".join(little_endian(bitstring.pack("16", field)) for field in self.color)
        period = little_endian(bitstring.pack("uint:32", self.period))
        cycles = little_endian(bitstring.pack("float:32", self.cycles))
        duty_cycle = little_endian(bitstring.pack("int:16", self.duty_cycle))
        waveform = little_endian(bitstring.pack("uint:8", self.waveform))
        payload = reserved_8 + transient + color + period + cycles + duty_cycle + waveform
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
        color = b"".join(little_endian(bitstring.pack("16", field)) for field in self.color)
        reserved1 = little_endian(bitstring.pack("16", self.reserved1))
        power_level = little_endian(bitstring.pack("16", self.power_level))
        try:
            label = b"".join(little_endian(bitstring.pack("8", c)) for c in self.label.encode('utf-8'))
        except ValueError: # because of differences in Python 2 and 3
            label = b"".join(little_endian(bitstring.pack("8", ord(c))) for c in self.label.encode('utf-8'))
        label_padding = b"".join(little_endian(bitstring.pack("8", 0)) for i in range(32-len(self.label)))
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
        self.payload_fields.append(("Power Level", self.power_level))
        self.payload_fields.append(("Duration", self.duration))
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

##### INFRARED MESSAGES #####

class LightGetInfrared(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(LightGetInfrared, self).__init__(MSG_IDS[LightGetInfrared], target_addr, source_id, seq_num, ack_requested, response_requested)

class LightStateInfrared(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.infrared_brightness = payload["infrared_brightness"]
        super(LightStateInfrared, self).__init__(MSG_IDS[LightStateInfrared], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Infrared Brightness", self.infrared_brightness))
        infrared_brightness = little_endian(bitstring.pack("16", self.infrared_brightness))
        payload = infrared_brightness
        return payload

class LightSetInfrared(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.infrared_brightness = payload["infrared_brightness"]
        super(LightSetInfrared, self).__init__(MSG_IDS[LightSetInfrared], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Infrared Brightness", self.infrared_brightness))
        infrared_brightness = little_endian(bitstring.pack("16", self.infrared_brightness))
        payload = infrared_brightness
        return payload

##### MULTIZONE MESSAGES #####

class MultiZoneStateMultiZone(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.count = payload["count"]
        self.index = payload["index"]
        self.color = payload["color"]
        super(MultiZoneStateMultiZone, self).__init__(MSG_IDS[MultiZoneStateMultiZone], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Count", self.count))
        self.payload_fields.append(("Index", self.index))
        self.payload_fields.append(("Color (HSBK)", self.color))
        count = little_endian(bitstring.pack("8", self.count))
        index = little_endian(bitstring.pack("8", self.index))
        payload = count + index
        for color in self.color:
            payload += b"".join(little_endian(bitstring.pack("16", field)) for field in color)
        return payload

class MultiZoneStateZone(Message): #503
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.count = payload["count"]
        self.index = payload["index"]
        self.color = payload["color"]
        super(MultiZoneStateZone, self).__init__(MSG_IDS[MultiZoneStateZone], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Count", self.count))
        self.payload_fields.append(("Index", self.index))
        self.payload_fields.append(("Color (HSBK)", self.color))
        count = little_endian(bitstring.pack("8", self.count))
        index = little_endian(bitstring.pack("8", self.index))
        color = b"".join(little_endian(bitstring.pack("16", field)) for field in self.color)
        payload = count + index + color
        return payload


class MultiZoneSetColorZones(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.start_index = payload["start_index"]
        self.end_index = payload["end_index"]
        self.color = payload["color"]
        self.duration = payload["duration"]
        self.apply = payload["apply"]
        super(MultiZoneSetColorZones, self).__init__(MSG_IDS[MultiZoneSetColorZones], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Start Index", self.start_index))
        self.payload_fields.append(("End Index", self.end_index))
        self.payload_fields.append(("Color", self.color))
        self.payload_fields.append(("Duration", self.duration))
        self.payload_fields.append(("Apply", self.apply))
        start_index = little_endian(bitstring.pack("8", self.start_index))
        end_index = little_endian(bitstring.pack("8", self.end_index))
        color = b"".join(little_endian(bitstring.pack("16", field)) for field in self.color)
        duration = little_endian(bitstring.pack("32", self.duration))
        apply = little_endian(bitstring.pack("8", self.apply))
        payload = start_index + end_index + color + duration + apply
        return payload

class MultiZoneGetColorZones(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.start_index = payload["start_index"]
        self.end_index = payload["end_index"]
        super(MultiZoneGetColorZones, self).__init__(MSG_IDS[MultiZoneGetColorZones], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Start Index", self.start_index))
        self.payload_fields.append(("End Index", self.end_index))
        start_index = little_endian(bitstring.pack("8", self.start_index))
        end_index = little_endian(bitstring.pack("8", self.end_index))
        payload = start_index + end_index
        return payload

class GetMultiZoneEffect(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        super(GetMultiZoneEffect, self).__init__(MSG_IDS[GetMultiZoneEffect], target_addr, source_id, seq_num, ack_requested, response_requested)

class SetMultiZoneEffect(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.instanceid = payload["instanceid"]
        self.effect_type = payload["type"]
        self.reserved1 = payload["reserved1"]
        self.speed = payload["speed"]
        self.duration = payload["duration"]
        self.reserved2 = payload["reserved2"]
        self.reserved3 = payload["reserved3"]
        self.parameters = payload["parameters"]
        super(SetMultiZoneEffect, self).__init__(MSG_IDS[SetMultiZoneEffect], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("InstanceId", self.instanceid))
        self.payload_fields.append(("Type", self.effect_type))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Speed", self.speed))
        self.payload_fields.append(("Duration", self.duration))
        self.payload_fields.append(("Reserved", self.reserved2))
        self.payload_fields.append(("Reserved", self.reserved3))
        self.payload_fields.append(("Parameters", self.parameters))
        instanceid = little_endian(bitstring.pack("32", self.instanceid))
        effect_type = little_endian(bitstring.pack("uint:8", self.effect_type))
        reserved1 = little_endian(bitstring.pack("16", self.reserved1))
        speed = little_endian(bitstring.pack("32", self.speed))
        duration = little_endian(bitstring.pack("64", self.duration))
        reserved2 = little_endian(bitstring.pack("32", self.reserved2))
        reserved3 = little_endian(bitstring.pack("32", self.reserved3))
        payload = instanceid + effect_type + reserved1 + speed + duration + reserved2 + reserved3
        for parameter in self.parameters:
            payload += little_endian(bitstring.pack("32", parameter))
        return payload

class StateMultiZoneEffect(Message):
    def __init__(self, target_addr, source_id, seq_num, payload, ack_requested=False, response_requested=False):
        self.instanceid = payload["instanceid"]
        self.effect_type = payload["type"]
        self.reserved1 = payload["reserved1"]
        self.speed = payload["speed"]
        self.duration = payload["duration"]
        self.reserved2 = payload["reserved2"]
        self.reserved3 = payload["reserved3"]
        self.parameters = payload["parameters"]
        super(StateMultiZoneEffect, self).__init__(MSG_IDS[StateMultiZoneEffect], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("InstanceId", self.instanceid))
        self.payload_fields.append(("Type", self.effect_type))
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Speed", self.speed))
        self.payload_fields.append(("Duration", self.duration))
        self.payload_fields.append(("Reserved", self.reserved2))
        self.payload_fields.append(("Reserved", self.reserved3))
        self.payload_fields.append(("Parameters", self.parameters))
        instanceid = little_endian(bitstring.pack("32", self.instanceid))
        effect_type = little_endian(bitstring.pack("uint:8", self.effect_type))
        reserved1 = little_endian(bitstring.pack("16", self.reserved1))
        speed = little_endian(bitstring.pack("32", self.speed))
        duration = little_endian(bitstring.pack("64", self.duration))
        reserved2 = little_endian(bitstring.pack("32", self.reserved2))
        reserved3 = little_endian(bitstring.pack("32", self.reserved3))
        payload = instanceid + effect_type + reserved1 + speed + duration + reserved2 + reserved3
        for parameter in self.parameters:
            payload += little_endian(bitstring.pack("32", parameter))
        return payload

##### TILE MESSAGES #####

class GetDeviceChain(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        target_addr = BROADCAST_MAC
        super(GetDeviceChain, self).__init__(MSG_IDS[GetDeviceChain], target_addr, source_id, seq_num, ack_requested, response_requested)

class StateDeviceChain(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        target_addr = BROADCAST_MAC
        self.start_index = payload["start_index"]
        self.total_count = payload["total_count"]
        self.tile_devices = payload["tile_devices"]
        super(StateDeviceChain, self).__init__(MSG_IDS[StateDeviceChain], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Start Index", self.start_index))
        self.payload_fields.append(("Total Count", self.total_count))
        self.payload_fields.append(("Tile Devices", self.tile_devices))
        start_idex = little_endian(bitstring.pack("uint:8", self.start_index))
        payload = start_idex
        for tile in self.tile_devices:
            reserved1 = little_endian(bitstring.pack("int:16", tile['reserved1']))
            reserved2 = little_endian(bitstring.pack("int:16", tile['reserved2']))
            reserved3 = little_endian(bitstring.pack("int:16", tile['reserved3']))
            reserved4 = little_endian(bitstring.pack("int:16", tile['reserved4']))
            user_x = little_endian(bitstring.pack("float:32", tile['user_x']))
            user_y = little_endian(bitstring.pack("float:32", tile['user_y']))
            width = little_endian(bitstring.pack("uint:8", tile['width']))
            height = little_endian(bitstring.pack("uint:8", tile['height']))
            reserved5 = little_endian(bitstring.pack("uint:8", tile['reserved5']))
            device_version_vendor = little_endian(bitstring.pack("uint:32", tile['device_version_vendor']))
            device_version_product = little_endian(bitstring.pack("uint:32", tile['device_version_product']))
            device_version_version = little_endian(bitstring.pack("uint:32", tile['device_version_version']))
            firmware_build = little_endian(bitstring.pack("uint:64", tile['firmware_build']))
            reserved6 = little_endian(bitstring.pack("uint:64", tile['reserved6']))
            firmware_version = little_endian(bitstring.pack("uint:32", tile['firmware_version']))
            reserved7 = little_endian(bitstring.pack("uint:32", tile['reserved7']))
            payload += reserved1 + reserved2 + reserved3 + reserved4 + user_x + user_y + width + height + reserved5 + device_version_vendor + device_version_product + device_version_version + firmware_build + reserved6 + firmware_version + reserved7
        total_count = little_endian(bitstring.pack("uint:8", self.total_count))
        payload += total_count
        return payload

class SetUserPosition(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        target_addr = BROADCAST_MAC
        self.tile_index = payload["tile_index"]
        self.reserved = payload["reserved"]
        self.user_x = payload["user_x"]
        self.user_y = payload["user_y"]
        super(SetUserPosition, self).__init__(MSG_IDS[SetUserPosition], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Tile Index", self.tile_index))
        self.payload_fields.append(("Reserved", self.reserved))
        self.payload_fields.append(("User X", self.user_x))
        self.payload_fields.append(("User Y", self.user_y))
        tile_index = little_endian(bitstring.pack("uint:8", self.tile_index))
        reserved = little_endian(bitstring.pack("uint:16", self.reserved))
        user_x = little_endian(bitstring.pack("float:32", self.user_x))
        user_y = little_endian(bitstring.pack("float:32", self.user_y))
        payload = tile_index + reserved + user_x + user_y
        return payload

class GetTileState64(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        target_addr = BROADCAST_MAC
        self.tile_index = payload["tile_index"]
        self.length = payload["length"]
        self.reserved = payload["reserved"]
        self.x = payload["x"]
        self.y = payload["y"]
        self.width = payload["width"]
        super(GetTileState64, self).__init__(MSG_IDS[GetTileState64], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Tile Index", self.tile_index))
        self.payload_fields.append(("Length", self.length))
        self.payload_fields.append(("Reserved", self.reserved))
        self.payload_fields.append(("X", self.x))
        self.payload_fields.append(("Y", self.y))
        self.payload_fields.append(("Width", self.width))
        tile_index = little_endian(bitstring.pack("uint:8", self.tile_index))
        length = little_endian(bitstring.pack("uint:8", self.length))
        reserved = little_endian(bitstring.pack("uint:8", self.reserved))
        x = little_endian(bitstring.pack("uint:8", self.x))
        y = little_endian(bitstring.pack("uint:8", self.y))
        width = little_endian(bitstring.pack("uint:8", self.width))
        payload = tile_index + length + reserved + x + y + width
        return payload

class StateTileState64(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        target_addr = BROADCAST_MAC
        self.tile_index = payload["tile_index"]
        self.reserved = payload["reserved"]
        self.x = payload["x"]
        self.y = payload["y"]
        self.width = payload["width"]
        self.colors = payload["colors"]
        super(StateTileState64, self).__init__(MSG_IDS[StateTileState64], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Tile Index", self.tile_index))
        self.payload_fields.append(("Reserved", self.reserved))
        self.payload_fields.append(("X", self.x))
        self.payload_fields.append(("Y", self.y))
        self.payload_fields.append(("Width", self.width))
        self.payload_fields.append(("Colors[64]", self.colors))
        tile_index = little_endian(bitstring.pack("uint:8", self.tile_index))
        reserved = little_endian(bitstring.pack("uint:8", self.reserved))
        x = little_endian(bitstring.pack("uint:8", self.x))
        y = little_endian(bitstring.pack("uint:8", self.y))
        width = little_endian(bitstring.pack("uint:8", self.width))
        payload = tile_index + reserved + x + y + width
        for color in self.colors:
            payload += b"".join(little_endian(bitstring.pack("16", field)) for field in color)
        return payload

class SetTileState64(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        target_addr = BROADCAST_MAC
        self.tile_index = payload["tile_index"]
        self.length = payload["length"]
        self.reserved = payload["reserved"]
        self.x = payload["x"]
        self.y = payload["y"]
        self.width = payload["width"]
        self.duration = payload["duration"]
        self.colors = payload["colors"]
        super(SetTileState64, self).__init__(MSG_IDS[SetTileState64], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Tile Index", self.tile_index))
        self.payload_fields.append(("Length", self.length))
        self.payload_fields.append(("Reserved", self.reserved))
        self.payload_fields.append(("X", self.x))
        self.payload_fields.append(("Y", self.y))
        self.payload_fields.append(("Width", self.width))
        self.payload_fields.append(("Duration", self.duration))
        self.payload_fields.append(("Colors", self.colors))
        tile_index = little_endian(bitstring.pack("uint:8", self.tile_index))
        length = little_endian(bitstring.pack("uint:8", self.length))
        reserved = little_endian(bitstring.pack("uint:8", self.reserved))
        x = little_endian(bitstring.pack("uint:8", self.x))
        y = little_endian(bitstring.pack("uint:8", self.y))
        width = little_endian(bitstring.pack("uint:8", self.width))
        duration = little_endian(bitstring.pack("32", self.duration))
        payload = tile_index + length + reserved + x + y + width + duration
        for color in self.colors:
            payload += b"".join(little_endian(bitstring.pack("16", field)) for field in color)
        return payload

class GetTileEffect(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        super(GetTileEffect, self).__init__(MSG_IDS[GetTileEffect], target_addr, source_id, seq_num, ack_requested, response_requested)

class SetTileEffect(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        self.reserved1 = payload["reserved1"]
        self.reserved2 = payload["reserved2"]
        self.instanceid = payload["instanceid"]
        self.effect_type = payload["type"]
        self.speed = payload["speed"]
        self.duration = payload["duration"]
        self.reserved3 = payload["reserved3"]
        self.reserved4 = payload["reserved4"]
        self.parameters = payload["parameters"]
        self.palette_count = payload["palette_count"]
        self.palette = payload["palette"]
        super(SetTileEffect, self).__init__(MSG_IDS[SetTileEffect], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("Reserved", self.reserved2))
        self.payload_fields.append(("InstanceId", self.instanceid))
        self.payload_fields.append(("Type", self.effect_type))
        self.payload_fields.append(("Speed", self.speed))
        self.payload_fields.append(("Duration", self.duration))
        self.payload_fields.append(("Reserved", self.reserved3))
        self.payload_fields.append(("Reserved", self.reserved4))
        self.payload_fields.append(("Parameters", self.parameters))
        self.payload_fields.append(("Palette Count", self.palette_count))
        self.payload_fields.append(("Palette", self.palette))
        reserved1 = little_endian(bitstring.pack("uint:8", self.reserved1))
        reserved2 = little_endian(bitstring.pack("uint:8", self.reserved2))
        instanceid = little_endian(bitstring.pack("32", self.instanceid))
        effect_type = little_endian(bitstring.pack("uint:8", self.effect_type))
        speed = little_endian(bitstring.pack("32", self.speed))
        duration = little_endian(bitstring.pack("64", self.duration))
        reserved3 = little_endian(bitstring.pack("32", self.reserved3))
        reserved4 = little_endian(bitstring.pack("32", self.reserved4))
        payload = reserved1 + reserved2 + instanceid + effect_type + speed + duration + reserved3 + reserved4
        for parameter in self.parameters:
            payload += little_endian(bitstring.pack("32", parameter))
        palette_count = little_endian(bitstring.pack("uint:8", self.palette_count))
        payload += palette_count
        for color in self.palette:
            payload += b"".join(little_endian(bitstring.pack("16", field)) for field in color)
        return payload

class StateTileEffect(Message):
    def __init__(self, target_addr, source_id, seq_num, payload={}, ack_requested=False, response_requested=False):
        self.reserved1 = payload["reserved1"]
        self.instanceid = payload["instanceid"]
        self.effect_type = payload["type"]
        self.speed = payload["speed"]
        self.duration = payload["duration"]
        self.reserved2 = payload["reserved2"]
        self.reserved3 = payload["reserved3"]
        self.parameters = payload["parameters"]
        self.palette_count = payload["palette_count"]
        self.palette = payload["palette"]
        super(StateTileEffect, self).__init__(MSG_IDS[StateTileEffect], target_addr, source_id, seq_num, ack_requested, response_requested)

    def get_payload(self):
        self.payload_fields.append(("Reserved", self.reserved1))
        self.payload_fields.append(("InstanceId", self.instanceid))
        self.payload_fields.append(("Type", self.effect_type))
        self.payload_fields.append(("Speed", self.speed))
        self.payload_fields.append(("Duration", self.duration))
        self.payload_fields.append(("Reserved", self.reserved2))
        self.payload_fields.append(("Reserved", self.reserved3))
        self.payload_fields.append(("Parameters", self.parameters))
        self.payload_fields.append(("Palette Count", self.palette_count))
        self.payload_fields.append(("Palette", self.palette))
        reserved1 = little_endian(bitstring.pack("uint:8", self.reserved1))
        instanceid = little_endian(bitstring.pack("32", self.instanceid))
        effect_type = little_endian(bitstring.pack("uint:8", self.effect_type))
        speed = little_endian(bitstring.pack("32", self.speed))
        duration = little_endian(bitstring.pack("64", self.duration))
        reserved2 = little_endian(bitstring.pack("32", self.reserved2))
        reserved3 = little_endian(bitstring.pack("32", self.reserved3))
        payload = reserved1 + instanceid + effect_type + speed + duration + reserved2 + reserved3
        for parameter in self.parameters:
            payload += little_endian(bitstring.pack("32", parameter))
        palette_count = little_endian(bitstring.pack("uint:8", self.palette_count))
        payload += palette_count
        for color in self.palette:
            payload += b"".join(little_endian(bitstring.pack("16", field)) for field in color)
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
                GetLocation: 48,
                StateLocation: 50,
                GetGroup: 51,
                StateGroup: 53,
                EchoRequest: 58,
                EchoResponse: 59,
                LightGet: 101,
                LightSetColor: 102,
                LightSetWaveform: 103,
                LightState: 107,
                LightGetPower: 116,
                LightSetPower: 117,
                LightStatePower: 118,
                LightGetInfrared: 120,
                LightStateInfrared: 121,
                LightSetInfrared: 122,
                MultiZoneSetColorZones: 501,
                MultiZoneGetColorZones: 502,
                MultiZoneStateZone: 503,
                MultiZoneStateMultiZone: 506,
                GetMultiZoneEffect: 507,
                SetMultiZoneEffect: 508,
                StateMultiZoneEffect: 509,
                GetDeviceChain: 701,
                StateDeviceChain: 702,
                SetUserPosition: 703,
                GetTileState64: 707,
                StateTileState64: 711,
                SetTileState64: 715,
                GetTileEffect: 718,
                SetTileEffect: 719,
                StateTileEffect: 720}

SERVICE_IDS = { 1: "UDP",
                2: "reserved",
                3: "reserved",
                4: "reserved"}

STR_MAP = { 65535: "On",
            0: "Off",
            None: "Unknown"}

ZONE_MAP = {0: "NO_APPLY",
            1:"APPLY",
            2:"APPLY_ONLY"}

TILE_EFFECT = {0: "OFF",
               1: "RESERVED",
               2: "MORPH",
               3: "FLAME"}

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
