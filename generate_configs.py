import yaml
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'))

with open("device_data.yaml") as f:
       devices = yaml.safe_load(f)["devices"]

template = env.get_template("template.j2")

for device in devices:
       config = template.render(hostname=device["hostname"], ip=device["ip"])
       with open(f"{device['hostname']}_config.txt", "w") as f:
              f.write(config)
              print(f"[GENERATED] {device['hostname']}_config.txt")
