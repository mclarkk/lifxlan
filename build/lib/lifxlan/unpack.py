# coding=utf-8
# unpack.py
# Author: Meghan Clark

import binascii
import struct

from .message import HEADER_SIZE_BYTES, Message
from .msgtypes import *


# Creates a LIFX Message out of packed binary data
# If the message type is not one of the officially released ones above, it will create just a Message out of it
# If it's not in the LIFX protocol format, uhhhhh...we'll put that on a to-do list.
def unpack_lifx_message(packed_message):
    header_str = packed_message[0:HEADER_SIZE_BYTES]
    payload_str = packed_message[HEADER_SIZE_BYTES:]

    size = struct.unpack("<H", header_str[0:2])[0]
    flags = struct.unpack("<H", header_str[2:4])[0]
    origin = (flags >> 14) & 3
    tagged = (flags >> 13) & 1
    addressable = (flags >> 12) & 1
    protocol = flags & 4095
    source_id = struct.unpack("<I", header_str[4:8])[0]
    target_addr = ":".join([('%02x' % b) for b in struct.unpack("<" + ("B"*6), header_str[8:14])])
    response_flags = struct.unpack("<B", header_str[22:23])[0]
    ack_requested = response_flags & 2
    response_requested = response_flags & 1
    seq_num = struct.unpack("<B", header_str[23:24])[0]
    message_type = struct.unpack("<H", header_str[32:34])[0]

    message = None
    if message_type == MSG_IDS[GetService]:
        message = GetService(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateService]:
        service = struct.unpack("<B", payload_str[0:1])[0]
        port = struct.unpack("<I", payload_str[1:5])[0]
        payload = {"service": service, "port": port}
        message = StateService(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetHostInfo]:
        message = GetHostInfo(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateHostInfo]:
        signal = struct.unpack("<f", payload_str[0:4])[0]
        tx = struct.unpack("<I", payload_str[4:8])[0]
        rx = struct.unpack("<I", payload_str[8:12])[0]
        reserved1 = struct.unpack("<h", payload_str[12:14])[0]
        payload = {"signal": signal, "tx": tx, "rx": rx, "reserved1": reserved1}
        message = StateHostInfo(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetHostFirmware]:
        message = GetHostFirmware(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateHostFirmware]:
        build = struct.unpack("<Q", payload_str[0:8])[0]
        reserved1 = struct.unpack("<Q", payload_str[8:16])[0]
        version = struct.unpack("<I", payload_str[16:20])[0]
        payload = {"build": build, "reserved1": reserved1, "version": version}
        message = StateHostFirmware(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetWifiInfo]:
        message = GetWifiInfo(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateWifiInfo]:
        signal = struct.unpack("<f", payload_str[0:4])[0]
        tx = struct.unpack("<I", payload_str[4:8])[0]
        rx = struct.unpack("<I", payload_str[8:12])[0]
        reserved1 = struct.unpack("<h", payload_str[12:14])[0]
        payload = {"signal": signal, "tx": tx, "rx": rx, "reserved1": reserved1}
        message = StateWifiInfo(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetWifiFirmware]:
        message = GetWifiFirmware(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateWifiFirmware]:
        build = struct.unpack("<Q", payload_str[0:8])[0]
        reserved1 = struct.unpack("<Q", payload_str[8:16])[0]
        version = struct.unpack("<I", payload_str[16:20])[0]
        payload = {"build": build, "reserved1": reserved1, "version": version}
        message = StateWifiFirmware(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetPower]:
        message = GetPower(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[SetPower]:
        power_level = struct.unpack("<H", payload_str[0:2])[0]
        payload = {"power_level": power_level}
        message = SetPower(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[StatePower]:
        power_level = struct.unpack("<H", payload_str[0:2])[0]
        payload = {"power_level": power_level}
        message = StatePower(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetLabel]:
        message = GetLabel(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[SetLabel]:
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff) for b in struct.unpack("<" + ("b"*32), payload_str[0:32])])).replace(b'\x00', b'')
        label = label.decode('utf-8')
        payload = {"label": label}
        message = SetLabel(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateLabel]:
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff) for b in struct.unpack("<" + ("b"*32), payload_str[0:32])])).replace(b'\x00', b'')
        label = label.decode('utf-8')
        payload = {"label": label}
        message = StateLabel(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetLocation]:
        message = GetLocation(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateLocation]:
        location = [b for b in struct.unpack("<" + ("B"*16), payload_str[0:16])]
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff) for b in struct.unpack("<" + ("b"*32), payload_str[16:48])])).replace(b'\x00', b'')
        label = label.decode('utf-8')
        updated_at = struct.unpack("<Q", payload_str[48:56])[0]
        payload = {"location": location, "label": label, "updated_at": updated_at}
        message = StateLocation(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetGroup]:
        message = GetGroup(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateGroup]:
        group = [b for b in struct.unpack("<" + ("B"*16), payload_str[0:16])]
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff) for b in struct.unpack("<" + ("b"*32), payload_str[16:48])])).replace(b'\x00', b'')
        label = label.decode('utf-8')
        updated_at = struct.unpack("<Q", payload_str[48:56])[0]
        payload = {"group": group, "label": label, "updated_at": updated_at}
        message = StateGroup(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetVersion]:
        message = GetVersion(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateVersion]:
        vendor = struct.unpack("<I", payload_str[0:4])[0]
        product = struct.unpack("<I", payload_str[4:8])[0]
        version = struct.unpack("<I", payload_str[8:12])[0]
        payload = {"vendor": vendor, "product": product, "version": version}
        message = StateVersion(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetInfo]:
        message = GetInfo(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateInfo]:
        time = struct.unpack("<Q", payload_str[0:8])[0]
        uptime = struct.unpack("<Q", payload_str[8:16])[0]
        downtime = struct.unpack("<Q", payload_str[16:24])[0]
        payload = {"time": time, "uptime": uptime, "downtime": downtime}
        message = StateInfo(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[Acknowledgement]:
        message = Acknowledgement(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[EchoRequest]:
        byte_array_len = len(payload_str)
        byte_array = [b for b in struct.unpack("<" + ("B"*byte_array_len), payload_str[0:byte_array_len])]
        payload = {"byte_array": byte_array}
        message = EchoRequest(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[EchoResponse]:
        byte_array_len = len(payload_str)
        byte_array = [b for b in struct.unpack("<" + ("B"*byte_array_len), payload_str[0:byte_array_len])]
        payload = {"byte_array": byte_array}
        message = EchoResponse(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightGet]:
        message = LightGet(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightSetColor]:
        reserved = struct.unpack("<B", payload_str[0:1])[0]
        color = struct.unpack("<" + ("H"*4), payload_str[1:9])
        duration = struct.unpack("<I", payload_str[9:13])[0]
        payload = {"color": color, "duration": duration}
        message = LightSetColor(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightState]:
        color = struct.unpack("<" + ("H"*4), payload_str[0:8])
        reserved1 = struct.unpack("<H", payload_str[8:10])[0]
        power_level = struct.unpack("<H", payload_str[10:12])[0]
        label = binascii.unhexlify("".join(["%2.2x" % (b & 0x000000ff) for b in struct.unpack("<" + ("b"*32), payload_str[12:44])])).replace(b'\x00', b'')
        label = label.decode('utf-8')
        reserved2 = struct.unpack("<Q", payload_str[44:52])[0]
        payload = {"color": color, "reserved1": reserved1, "power_level": power_level, "label": label, "reserved2": reserved2}
        message = LightState(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightGetPower]:
        message = LightGetPower(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightSetPower]:
        power_level = struct.unpack("<H", payload_str[0:2])[0]
        duration = struct.unpack("<I", payload_str[2:6])[0]
        payload = {"power_level": power_level, "duration": duration}
        message = LightSetPower(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightStatePower]:
        power_level = struct.unpack("<H", payload_str[0:2])[0]
        payload = {"power_level": power_level}
        message = LightStatePower(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightGetInfrared]:  # 120
        message = LightGetInfrared(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightStateInfrared]:  # 121
        infrared_brightness = struct.unpack("<H", payload_str[0:2])[0]
        payload = {"infrared_brightness": infrared_brightness}
        message = LightStateInfrared(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[LightSetInfrared]:  # 122
        infrared_brightness = struct.unpack("<H", payload_str[0:2])[0]
        payload = {"infrared_brightness": infrared_brightness}
        message = LightSetInfrared(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[MultiZoneSetColorZones]: #501
        start_index = struct.unpack("<c", payload_str[0:1])[0]
        start_index = ord(start_index) # 8 bit
        end_index = struct.unpack("<c", payload_str[1:2])[0]
        end_index = ord(end_index) #8 bit
        color = struct.unpack("<" + ("H" * 4), payload_str[2:10])
        duration = struct.unpack("<I", payload_str[10:14])[0]
        apply = struct.unpack("<c", payload_str[14:15])[0]
        apply = ord(apply) #8 bit
        payload = {"start_index": start_index, "end_index": end_index, "color": color, "duration": duration, "apply": apply}
        message = MultiZoneSetColorZones(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[MultiZoneGetColorZones]: #502
        start_index = struct.unpack("<c", payload_str[0:1])[0]
        start_index = ord(start_index) # 8 bit
        end_index = struct.unpack("<c", payload_str[1:2])[0]
        end_index = ord(end_index) #8 bit
        payload = {"start_index": start_index, "end_index": end_index}
        message = MultiZoneGetColorZones(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[MultiZoneStateZone]: #503
        count = struct.unpack("<c", payload_str[0:1])[0]
        count = ord(count) # 8 bit
        index = struct.unpack("<c", payload_str[1:2])[0]
        index = ord(index) #8 bit
        color = struct.unpack("<" + ("H" * 4), payload_str[2:10])
        payload = {"count": count, "index": index, "color": color}
        message = MultiZoneStateZone(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[MultiZoneStateMultiZone]: #506
        count = struct.unpack("<c", payload_str[0:1])[0]
        count = ord(count) # 8 bit
        index = struct.unpack("<c", payload_str[1:2])[0]
        index = ord(index) #8 bit
        colors = []
        for i in range(8):
            color = struct.unpack("<" + ("H" * 4), payload_str[2+(i*8):10+(i*8)])
            colors.append(color)
        payload = {"count": count, "index": index, "color": colors}
        message = MultiZoneStateMultiZone(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetDeviceChain]: #701
        message = GetDeviceChain(target_addr, source_id, seq_num, {}, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateDeviceChain]: #702
        start_index = struct.unpack("<B", payload_str[0:1])[0]
        tile_devices = []
        tilesize_bytes = 55
        for i in range(16):
            offset = (i * tilesize_bytes)
            tile = {"reserved1": struct.unpack("<h", payload_str[1+offset:3+offset])[0],
                    "reserved2": struct.unpack("<h", payload_str[3+offset:5+offset])[0],
                    "reserved3": struct.unpack("<h", payload_str[5+offset:7+offset])[0],
                    "reserved4": struct.unpack("<h", payload_str[7+offset:9+offset])[0],
                    "user_x": struct.unpack("<f", payload_str[9+offset:13+offset])[0],
                    "user_y": struct.unpack("<f", payload_str[13+offset:17+offset])[0],
                    "width": struct.unpack("<B", payload_str[17+offset:18+offset])[0],
                    "height": struct.unpack("<B", payload_str[18+offset:19+offset])[0],
                    "reserved5": struct.unpack("<B", payload_str[19+offset:20+offset])[0],
                    "device_version_vendor": struct.unpack("<I", payload_str[20+offset:24+offset])[0],
                    "device_version_product": struct.unpack("<I", payload_str[24+offset:28+offset])[0],
                    "device_version_version": struct.unpack("<I", payload_str[28+offset:32+offset])[0],
                    "firmware_build": struct.unpack("<Q", payload_str[32+offset:40+offset])[0],
                    "reserved6": struct.unpack("<Q", payload_str[40+offset:48+offset])[0],
                    "firmware_version": struct.unpack("<I", payload_str[48+offset:52+offset])[0],
                    "reserved7": struct.unpack("<I", payload_str[52+offset:56+offset])[0]}
            tile_devices.append(tile)
        total_count = struct.unpack("<B", payload_str[881:882])[0]
        payload = {"start_index": start_index, "total_count": total_count, "tile_devices": tile_devices}
        message = StateDeviceChain(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[SetUserPosition]: #703
        tile_index = struct.unpack("<B", payload_str[0:1])[0]
        reserved = struct.unpack("<H", payload_str[1:3])[0]
        user_x = struct.unpack("<f", payload_str[3:7])[0]
        user_y = struct.unpack("<f", payload_str[7:11])[0]
        payload = {"tile_index": tile_index, "reserved": reserved, "user_x": user_x, "user_y": user_y}
        message = SetUserPosition(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[GetTileState64]: #707
        tile_index = struct.unpack("<B", payload_str[0:1])[0]
        length = struct.unpack("<B", payload_str[1:2])[0]
        reserved = struct.unpack("<B", payload_str[2:3])[0]
        x = struct.unpack("<B", payload_str[3:4])[0]
        y = struct.unpack("<B", payload_str[4:5])[0]
        width = struct.unpack("<B", payload_str[5:6])[0]
        payload = {"tile_index": tile_index, "length": length, "reserved": reserved, "x": x, "y": y, "width": width}
        message = GetTileState64(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[StateTileState64]: #711
        tile_index = struct.unpack("<B", payload_str[0:1])[0]
        reserved = struct.unpack("<B", payload_str[1:2])[0]
        x = struct.unpack("<B", payload_str[2:3])[0]
        y = struct.unpack("<B", payload_str[3:4])[0]
        width = struct.unpack("<B", payload_str[4:5])[0]
        colors = []
        for i in range(64):
            color = struct.unpack("<" + ("H" * 4), payload_str[5+(i*8):13+(i*8)])
            colors.append(color)
        payload = {"tile_index": tile_index, "reserved": reserved, "x": x, "y": y, "width": width, "colors": colors}
        message = StateTileState64(target_addr, source_id, seq_num, payload, ack_requested, response_requested)

    elif message_type == MSG_IDS[SetTileState64]: #715
        tile_index = struct.unpack("<B", payload_str[0:1])[0]
        length = struct.unpack("<B", payload_str[1:2])[0]
        reserved = struct.unpack("<B", payload_str[2:3])[0]
        x = struct.unpack("<B", payload_str[3:4])[0]
        y = struct.unpack("<B", payload_str[4:5])[0]
        width = struct.unpack("<B", payload_str[5:6])[0]
        duration = struct.unpack("<I", payload_str[6:10])[0]
        colors = []
        for i in range(64):
            color = struct.unpack("<" + ("H" * 4), payload_str[10+(i*8):18+(i*8)])
            colors.append(color)
        payload = {"tile_index": tile_index, "length": length, "reserved": reserved, "x": x, "y": y, "width": width, "duration": duration, "colors": colors}
        message = SetTileState64(target_addr, source_id, seq_num, payload, ack_requested, response_requested)


    else:
        message = Message(message_type, target_addr, source_id, seq_num, ack_requested, response_requested)

    message.size = size
    message.origin = origin
    message.tagged = tagged
    message.addressable = addressable
    message.protocol = protocol
    message.source_id = source_id
    message.header = header_str
    message.payload = payload_str
    message.packed_message = packed_message

    return message
