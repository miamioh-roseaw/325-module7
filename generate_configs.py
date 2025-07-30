# Import required modules
import yaml  # For loading YAML configuration files
import os  # For interacting with the operating system (e.g., environment variables, directories)
from jinja2 import Environment, FileSystemLoader  # For using Jinja2 templates
from netmiko import ConnectHandler  # For SSH automation with network devices
import re  # Optional, included in case regex is needed later

# === Load Device Inventory ===
# Open the devices.yaml file and load the 'devices' section into the 'inventory' dictionary
with open("devices.yaml") as f:
    inventory = yaml.safe_load(f)["devices"]

# === Load Device-Specific Configuration Variables ===
# Open the device_config.yaml file and load the 'config' section into 'config_data'
with open("device_config.yaml") as f:
    config_data = yaml.safe_load(f)["config"]

# === Initialize the Jinja2 Templating Engine ===
# Tell Jinja2 to look for templates in the current directory (".")
env = Environment(loader=FileSystemLoader("."))

# === Create Output Directory ===
# Make a folder called "rendered_configs" if it doesn’t already exist
os.makedirs("rendered_configs", exist_ok=True)

# === Loop Through All Devices ===
# This will generate and push a config for each device listed in devices.yaml
for name, device in inventory.items():
    print(f"[INFO] Rendering config for {name}...")

    try:
        # === Prepare Device-Specific Variables for the Template ===
        # Get the configuration data for this specific device from device_config.yaml
        device_vars = config_data.get(name, {})

        # Determine whether the device is a router or a switch (default to router if not defined)
        device_type = device.get("type", "router")

        # Choose the correct Jinja2 template file based on device type
        template_file = "switch_template.j2" if device_type == "switch" else "router_template.j2"

        # === Render the Template ===
        # Load the template
        template = env.get_template(template_file)

        # Fill in the template with the device-specific variables
        rendered_config = template.render(**device_vars)

        # === Save Rendered Config to File ===
        # Store the rendered config as a .cfg file under rendered_configs/
        config_path = f"rendered_configs/{name}.cfg"
        with open(config_path, "w") as f:
            f.write(rendered_config)

        print(f"[SUCCESS] Saved config to {config_path}")

        # === Connect to Device Using Netmiko ===
        # Use credentials from Jenkins environment variables to establish SSH session
        conn = ConnectHandler(
            device_type="cisco_ios",  # Specifies type of device for Netmiko
            ip=device["hostname"],  # IP address from devices.yaml
            username=os.environ["CISCO_USER"],  # Pulled from Jenkins credential binding
            password=os.environ["CISCO_PASS"],
            secret=os.environ["CISCO_PASS"],  # Enable password, same as login in this case
        )

        # Enter privileged EXEC mode (enable mode)
        conn.enable()

        print(f"[INFO] Pushing config to {name}...")

        # === Send Configuration Commands ===
        # Split the rendered config into individual lines and send them to the device
        output = conn.send_config_set(rendered_config.splitlines(), read_timeout=60)
        print(output)

        # === Save Configuration and Disconnect ===
        conn.save_config()  # Equivalent to "write memory"
        conn.disconnect()   # Log out from the device
        print(f"[✓] Config pushed to {name}")

    except Exception as e:
        # Catch and print any errors encountered during rendering or pushing
        print(f"[ERROR] Failed with {name}: {e}")
