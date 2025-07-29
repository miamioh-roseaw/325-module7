import yaml
import os
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler

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

        # Load appropriate template
        template = env.get_template(template_file)
        rendered_config = template.render(**device_vars)

        # Save rendered config
        config_file = f"rendered_configs/{name}.cfg"
        with open(config_file, "w") as f:
            f.write(rendered_config)
        print(f"[SUCCESS] Saved config to {config_file}")

        # Push config via Netmiko
        conn = ConnectHandler(
            device_type="cisco_ios",
            ip=device["hostname"],
            username=device["username"],
            password=device["password"],
        )
        output = conn.send_config_set(rendered_config.splitlines())
        print(f"[SUCCESS] Applied config to {name}")
        print(output)

        conn.save_config()
        conn.disconnect()

    except Exception as e:
        print(f"[ERROR] Failed with {name}: {e}")
