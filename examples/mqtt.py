""" Example of using the LIFX LAN library to control LIFX devices via MQTT"""
import argparse
import threading

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from lifxlan import Device as LifxDevice
from lifxlan import LifxLAN


class MQTTLifxDevice:
    """Base class for LIFX devices that will be controlled via MQTT"""

    def __init__(
        self, client: mqtt.Client, device: LifxDevice, refresh_interval: float = 5.0
    ) -> None:
        self.client = client
        self.device = device
        self.refresh_interval = refresh_interval
        self.device.refresh()
        self.serial = self.device.mac_addr.replace(":", "")

        if self.device.is_switch():
            self._init_switch()
        else:
            print(
                f"Device {self.device.get_label()} is not a switch, only switches are supported at this time"
            )
            raise NotImplementedError

        self.refresh()

    def _init_switch(self):
        # For each switch, determine which relays we should control.
        # We'll use the action target_type relay to see which relays are available.
        _, _, _, buttons = self.device.get_buttons()
        self.device.relays = []
        for button in buttons:
            for action in button["actions"]:
                if action["target_type"] == "Relays":
                    for relay_index in action["relays"]:
                        power = self.device.get_relay_power(relay_index)
                        self.device.relays.append(
                            {"relay": relay_index, "power": power}
                        )

        # For each relay, subscribe to the MQTT topics and publish states
        for relay in self.device.relays:
            power = relay["power"]
            relay["state_topic"] = f"lifx/{self.serial}/relay{relay['relay']}"
            relay["set_topic"] = f"{relay['state_topic']}/set"
            relay["availability_topic"] = f"{relay['state_topic']}/available"

            result, mid = self.client.subscribe(
                [
                    (relay["state_topic"], 0),
                    (relay["set_topic"], 0),
                    (relay["availability_topic"], 0),
                ]
            )
            print(
                f'Subscribed to {relay["state_topic"], relay["set_topic"], relay["availability_topic"]} with result {result} and mid {mid}'
            )
            self.client.publish(relay["availability_topic"], "online", retain=True)
            self.client.publish(relay["state_topic"], relay["power"], retain=True)

    def refresh(self):
        """Refresh the device state and publish the new state to MQTT"""
        try:
            self.device.refresh()
            for relay in self.device.relays:
                relay["power"] = self.device.get_relay_power(relay["relay"])
                self.client.publish(relay["state_topic"], relay["power"], retain=True)
        except Exception as e:
            print(f"Error refreshing device {self.device.get_label()}: {e}")
        threading.Timer(self.refresh_interval, self.refresh).start()

    def on_message_callback(self, _client, _userdata, message: MQTTMessage):
        """Callback for MQTT messages"""
        print(f"Message received: {message.topic} {message.payload}")
        relay = next(
            (r for r in self.device.relays if r["set_topic"] == message.topic), None
        )
        if relay is None:
            print(f"No relay found for topic {message.topic}")
            return
        self.device.set_relay_power(relay["relay"], message.payload.decode())


def _command_line_handler():
    """Parse command line arguments and execute the appropriate action."""
    parser = argparse.ArgumentParser(description="MQTT LIFX connector")
    parser.add_argument("-b", "--broker", help="MQTT broker address", required=True)
    parser.add_argument("-p", "--port", help="MQTT broker port", default=1883, type=int)
    parser.add_argument("-U", "--username", help="MQTT broker username", required=True)
    parser.add_argument("-P", "--password", help="MQTT broker password", required=True)
    parser.add_argument(
        "-i", "--interval", help="Refresh interval", default=5, type=float
    )
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")

    args = parser.parse_args()

    lifx = LifxLAN(verbose=args.verbose)
    switches = lifx.get_switches()

    client = mqtt.Client()
    client.username_pw_set(args.username, args.password)
    client.connect(args.broker, args.port)

    print(f"Found {len(switches)} switches:")
    for switch in switches:
        print(f"\t{switch.get_label()}")
        switch.mqtt = MQTTLifxDevice(client, switch, args.interval)
        for relay in switch.mqtt.device.relays:
            client.message_callback_add(
                relay["set_topic"], switch.mqtt.on_message_callback
            )

    client.loop_forever()


if __name__ == "__main__":
    _command_line_handler()
