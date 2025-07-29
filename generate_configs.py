import yaml
from netmiko import ConnectHandler
import os

# Load inventory (devices.yaml)
with open("devices.yaml") as f:
    inventory = yaml.safe_load(f)["devices"]

# Load configuration data (device_config.yaml)
with open("device_config.yaml") as f:
    config_data = yaml.safe_load(f)["config"]

# Loop through each device
for name, device in inventory.items():
    print(f"[INFO] Connecting to {name} at {device['hostname']}...")
    try:
        conn = ConnectHandler(
            device_type="cisco_ios",
            ip=device["hostname"],
            username=device["username"],
            password=device["password"],
        )

        # Build config commands
        config_cmds = []
        device_config = config_data.get(name, {})

        if "hostname" in device_config:
            config_cmds.append(f"hostname {device_config['hostname']}")

        if "banner" in device_config:
            config_cmds.append(f"banner motd ^{device_config['banner']}^")

        if "vlans" in device_config:
            for vlan in device_config["vlans"]:
                config_cmds.append(f"vlan {vlan['id']}")
                config_cmds.append(f"name {vlan['name']}")

        # Send config
        output = conn.send_config_set(config_cmds)
        print(f"[SUCCESS] Configuration applied to {name}")
        print(output)

        # Save config
        conn.save_config()
        conn.disconnect()

    except Exception as e:
        print(f"[ERROR] Failed to configure {name}: {e}")
