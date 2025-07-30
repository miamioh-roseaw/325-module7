import yaml
import os
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler
import re

# Load device inventory (devices.yaml)
with open("devices.yaml") as f:
    inventory = yaml.safe_load(f)["devices"]

# Load configuration data (device_config.yaml)
with open("device_config.yaml") as f:
    config_data = yaml.safe_load(f)["config"]

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader("."))

# Ensure output directory exists
os.makedirs("rendered_configs", exist_ok=True)

# Loop through each device
for name, device in inventory.items():
    print(f"[INFO] Rendering config for {name}...")
    try:
        device_vars = config_data.get(name, {})
        device_type = device.get("type", "router")
        template_file = "switch_template.j2" if device_type == "switch" else "router_template.j2"

        # Render config
        template = env.get_template(template_file)
        rendered_config = template.render(**device_vars)

        config_path = f"rendered_configs/{name}.cfg"
        with open(config_path, "w") as f:
            f.write(rendered_config)
        print(f"[SUCCESS] Saved config to {config_path}")

        # Push config with Netmiko
        conn = ConnectHandler(
            device_type="cisco_ios",
            ip=device["hostname"],
            username=os.environ["CISCO_USER"],
            password=os.environ["CISCO_PASS"],
            secret=os.environ["CISCO_PASS"],
        )
        conn.enable()

        print(f"[INFO] Pushing config to {name}...")
        output = conn.send_config_set(rendered_config.splitlines(), read_timeout=60)
        print(output)

        conn.save_config()
        conn.disconnect()
        print(f"[✓] Config pushed to {name}")

    except Exception as e:
        print(f"[ERROR] Failed with {name}: {e}")
