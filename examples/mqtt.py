""" Example of using the LIFX LAN library to control LIFX devices via MQTT """
import argparse
import json
import signal
import sys
import threading
from pathlib import Path

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from lifxlan import Device as LifxDevice
from lifxlan import LifxLAN

DEFAULT_TOPIC_STRUCTURE = "lifx/{serial}/{type}{index}/{suffix}"


def signal_handler(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# Function to allow the user to define the order of fields in the topic
def build_topic(topic_structure: str, type: str, serial: str, index: str, suffix: str):
    return topic_structure.format(type=type, serial=serial, index=index, suffix=suffix)


def config_topic(topic_structure: str, type: str, serial: str, index: str):
    return build_topic(topic_structure, type, serial, index, "config")


def state_topic(topic_structure: str, type: str, serial: str, index: str):
    return build_topic(topic_structure, type, serial, index, "state")


def available_topic(topic_structure: str, type: str, serial: str, index: str):
    return build_topic(topic_structure, type, serial, index, "available")


def set_topic(topic_structure: str, type: str, serial: str, index: str):
    return build_topic(topic_structure, type, serial, index, "set")


class MQTTLifxDevice:
    """Class for LIFX devices that will be controlled via MQTT"""

    _DEFAULT_REFRESH_INTERVAL: float = 5.0

    def __init__(self, client: mqtt.Client, device: LifxDevice) -> None:
        self.client = client
        self.device = device
        self.refresh_interval = MQTTLifxDevice._DEFAULT_REFRESH_INTERVAL
        self.device.refresh()
        self.serial = self.device.mac_addr.replace(":", "")

        if self.device.is_switch():
            self._init_switch()
        else:
            print(
                f"Device {self.device.get_label()} is not a switch, only switches are supported at this time"
            )
            raise NotImplementedError

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

    def subscribe_and_announce(self):
        """Subscribe to MQTT topics"""

        for relay in self.device.relays:
            result, mid = self.client.subscribe(relay["set_topic"])
            print(
                f'Subscribed to {relay["set_topic"]} with result {result} and mid {mid}'
            )
            self.client.message_callback_add(
                relay["set_topic"], self.on_message_callback
            )
            self.client.publish(relay["available_topic"], "online", retain=True)
            self.client.publish(relay["state_topic"], relay["power"], retain=True)
            self.client.publish(
                relay["config_topic"], relay["config"]["payload"], retain=True
            )

    def set_refresh_interval(self, interval: float):
        """Set the refresh interval"""
        self.refresh_interval = interval

    def refresh(self, continuous: bool = True):
        """Refresh the device state and publish the new state to MQTT"""
        try:
            self.device.refresh()
            for relay in self.device.relays:
                relay["power"] = self.device.get_relay_power(relay["relay"])
                self.client.publish(relay["state_topic"], relay["power"], retain=True)
        except Exception as e:
            print(f"Error refreshing device {self.device.get_label()}: {e}")
        if continuous:
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
        try:
            self.device.set_relay_power(relay["relay"], message.payload.decode())
        except Exception as e:
            print(f"Error setting relay {relay['relay']}: {e}")
            print("Trying again in 5 seconds")
            threading.Timer(5.0, self.on_message_callback, [message]).start()


def _config_file() -> str:
    """Return the path to the config file"""
    return Path("~/.config/mqtt-lifx-connector.json").expanduser()


def _wizard_handler(args):
    """
    Run the wizard to generate a config file

    Ask for the following MQTT settings:
    - MQTT broker address
    - MQTT broker port
    - MQTT username
    - MQTT password
    - Refresh interval
    - Topic structure

    Scan for lifx relays on lifx switches and for each one:
    - Print the switch name and relay number
    - Ask what type of device is attached to the relay
    - Ask for a name for the device

    """

    print("MQTT LIFX connector wizard\n")
    if _config_file().exists():
        config = json.loads(_config_file().read_text())
        mqtt_config = config["mqtt"]
    else:
        mqtt_config = {
            "broker": "127.0.0.1",
            "port": 1883,
            "username": "",
            "password": "",
            "interval": 5.0,
            "topic_structure": DEFAULT_TOPIC_STRUCTURE,
        }
        config = {"mqtt": mqtt_config, "switches": []}

    print("MQTT parameters:")
    config["mqtt"] = {
        "broker": input(f"\tMQTT broker address [{mqtt_config['broker']}]: ")
        or mqtt_config["broker"],
        "port": int(
            input(f"\tMQTT broker port [{mqtt_config['port']}]: ")
            or mqtt_config["port"]
        ),
        "username": input(f"\tMQTT username [{mqtt_config['username']}]: ")
        or mqtt_config["username"],
        "password": input("\tMQTT password [*]: ") or mqtt_config["password"],
        "interval": float(
            input(f"\tRefresh interval [{mqtt_config['interval']}]s: ")
            or mqtt_config["interval"]
        ),
        "topic_structure": input(
            f"\tTopic structure [{mqtt_config['topic_structure']}]: "
        )
        or mqtt_config["topic_structure"],
    }

    print("\nLIFX switches:")
    lifx = LifxLAN(verbose=args.verbose)
    switches = lifx.get_switches()
    for switch in switches:
        switch.refresh()
        switch.serial = switch.mac_addr.replace(":", "")
        print(f"\t{switch.label} ({switch.serial})")
        switch.config = next(
            (s for s in config["switches"] if s["serial"] == switch.serial),
            {
                "name": switch.label,
                "serial": switch.serial,
                "relays": [],
            },
        )
        _, _, _, buttons = switch.get_buttons()
        for button in buttons:
            for action in button["actions"]:
                if action["target_type"] == "Relays":
                    for relay_index in action["relays"]:
                        print(f"\t\tRelay {relay_index}")
                        i = next(
                            (
                                index
                                for (index, r) in enumerate(switch.config["relays"])
                                if r["relay"] == relay_index
                            ),
                            None,
                        )
                        if i is None:
                            prev_name = ""
                            prev_type = "light"
                        else:
                            prev_name = switch.config["relays"][i]["name"]
                            prev_type = switch.config["relays"][i]["type"]

                        relay = {
                            "relay": relay_index,
                            "name": input(f"\t\t\tDevice name [{prev_name}]: ")
                            or prev_name,
                            "type": input(f"\t\t\tDevice type [{prev_type}]: ").lower()
                            or prev_type,
                        }
                        if i is None:
                            switch.config["relays"].append(relay)
                        else:
                            switch.config["relays"][i] = relay

    config["switches"] = []
    for switch in switches:
        switch.config["relays"] = sorted(
            switch.config["relays"], key=lambda r: r["relay"]
        )
        config["switches"].append(switch.config)

    config_str = json.dumps(config, indent=4)
    print(config_str)
    with open(_config_file(), "w") as f:
        f.write(config_str)


def _run_handler(args):
    """Run the MQTT LIFX connector in the foreground"""

    # Check for a config file and load it
    # If no config file, run the wizard
    if not _config_file().exists():
        return _wizard_handler(args)

    config = json.loads(_config_file().read_text())
    print("Loaded config:")
    for switch in config["switches"]:
        print(f"\tSwitch {switch['serial']}: {switch['name']}")
        for relay in switch["relays"]:
            print(f"\t\tRelay {relay['relay']}: {relay['name']}")

    lifx = LifxLAN(verbose=args.verbose)
    switches = lifx.get_switches()

    if len(switches) != len(config["switches"]):
        print(
            f"Found {len(switches)} switches but config has {len(config['switches'])} switches"
        )
        print("Run the wizard")
        return

    client = mqtt.Client()
    client.username_pw_set(config["mqtt"]["username"], config["mqtt"]["password"])
    client.connect(config["mqtt"]["broker"], config["mqtt"]["port"])

    print("Discovered devices:")
    for switch in switches:
        switch.mqtt = MQTTLifxDevice(client, switch)
        switch.mqtt.set_refresh_interval(config["mqtt"]["interval"])
        try:
            switch.refresh()
        except Exception as e:
            print(f"Error refreshing switch {switch.label}: {e}")
            continue
        switch.serial = switch.mac_addr.replace(":", "")
        print(f"\tSwitch {switch.serial}: {switch.label}")
        if switch.serial not in [s["serial"] for s in config["switches"]]:
            print(f"Switch {switch.serial} not found in config")
            print("Run the wizard")
            return

        switch.config = next(
            s for s in config["switches"] if s["serial"] == switch.serial
        )

        for relay in switch.relays:
            if relay["relay"] not in [r["relay"] for r in switch.config["relays"]]:
                print(f"\t\tRelay {relay['relay']} not found in config")
                print("Run the wizard to configure - skipping for now")
                continue

            relay["config"] = next(
                r for r in switch.config["relays"] if r["relay"] == relay["relay"]
            )

            print(f"\t\tRelay {relay['relay']}: {relay['config']['name']}")
            for topic in ["state", "set", "available", "config"]:
                func = globals()[f"{topic}_topic"]
                relay[f"{topic}_topic"] = func(
                    config["mqtt"]["topic_structure"],
                    relay["config"]["type"],
                    switch.serial,
                    relay["relay"],
                )

            relay["config"]["payload"] = json.dumps(
                {
                    "unique_id": f"{switch.serial}_{relay['relay']}",
                    "name": relay["config"]["name"],
                    "command_topic": relay["set_topic"],
                    "state_topic": relay["state_topic"],
                    "availability_topic": relay["available_topic"],
                    "payload_on": 65535,
                    "payload_off": 0,
                    "retain": True,
                }
            )
        switch.mqtt.subscribe_and_announce()
        switch.mqtt.refresh(continuous=True)

    print("Configured devices all found")

    client.loop_forever()


def _command_line_handler():
    """Parse command line arguments and execute the appropriate action."""

    class NoAction(argparse.Action):
        def __init__(self, **kwargs):
            kwargs.setdefault("default", argparse.SUPPRESS)
            kwargs.setdefault("nargs", 0)
            super(NoAction, self).__init__(**kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            pass

    parser = argparse.ArgumentParser(description="MQTT LIFX connector")
    parser.register("action", "none", NoAction)

    command_options = {
        "wizard": "Run the wizard to generate a config file",
        "run": "Run the MQTT LIFX connector in the foreground",
    }

    parser.add_argument(
        "command",
        metavar="COMMAND",
        help=f"Command to execute: {' '.join(command_options.keys())}",
        nargs=1,
        choices=command_options.keys(),
    )

    command_group = parser.add_argument_group(title="Command options")
    for option in command_options:
        command_group.add_argument(
            f"{option}",
            action="none",
            help=command_options[option],
        )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print verbose output"
    )

    args = parser.parse_args()

    match args.command[0]:
        case "wizard":
            _wizard_handler(args)
        case "run":
            _run_handler(args)
            print(f"Unknown command {args.command[0]}")
            parser.print_help()


if __name__ == "__main__":
    _command_line_handler()
