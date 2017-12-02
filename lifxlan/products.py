# coding=utf-8
import json
import os

path = os.path.dirname(__file__)
products_file = os.path.join(path, "products.json")

with open(products_file) as f:
    data = json.loads(f.read())

product_map  = {}
features_map = {}

# Identifies which products are lights.
# Currently all LIFX products that speak the LAN protocol are lights.
# However, the protocol was written to allow addition of other kinds
# of devices, so it's important to be able to differentiate.
light_products = []

for product in data[0]["products"]:
    pid = product["pid"]
    product_map[pid]  = product["name"]
    features_map[pid] = product["features"]
    light_products.append(pid)
