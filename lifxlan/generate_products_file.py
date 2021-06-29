#!/usr/bin/env python3
# This python 3.6+ script is a quick products.py file generator

import json
import re
import http.client
import sys

hev = [90, 99]
relays = [70, 71, 89]
buttons = [70, 71, 89]

def main():
    conn = http.client.HTTPSConnection("raw.githubusercontent.com")
    conn.request("GET", "/LIFX/products/master/products.json")
    resp = conn.getresponse()

    if resp.status != 200:
        print(f"Error getting products.json: {resp.status} {resp.reason}")
        sys.exit(1)

    try:
        data = json.loads(resp.read())
    except Exception as ex:
        print(f"Failed to parse the input: {ex}")
        sys.exit(1)
    finally:
        conn.close()

    print("# coding=utf-8")
    print("product_map = {")

    mapdata = data[0]['products']
    num_products = len(mapdata)

    for product in mapdata:
        print(f"               {product['pid']}: \"{product['name']}\",")
    print(f"               None: \"Unknown product\"")

    print("              }")
    print("")
    print("# Identifies which products are lights.")

    products = []
    for product in mapdata:
        if product['pid'] not in relays:
            products.append(product['pid'])

    lightproducts = ', '.join(map(str, products))
    print(f"light_products = [{lightproducts}]")
    print("")

    print("# Identifies which products are switches.")
    print(f"switch_products = {relays}")
    print("")


    print("features_map = {")
    #i = 0
    for product in mapdata:
        #i += 1
        if 'temperature_range' in product['features'] and product['features']['temperature_range'][0] != product['features']['temperature_range'][1]:
            temp = True
        else:
            temp = False

        print(f"                {product['pid']}: {{\t\t\t\t\t\t# {product['name']}")
        print(f"                     \"color\": {product['features']['color']},")
        print(f"                     \"temperature\": {temp},")
        print(f"                     \"infrared\": {product['features']['infrared']},")
        print(f"                     \"multizone\": {product['features']['multizone']},")
        print(f"                     \"chain\": {product['features']['chain']},")
        print(f"                     \"matrix\": {product['features']['matrix']},")
        if 'temperature_range' in product['features']:
            print(f"                     \"min_kelvin\": {product['features']['temperature_range'][0]},")
            print(f"                     \"max_kelvin\": {product['features']['temperature_range'][1]},")
        print(f"                     \"hev\": {product['pid'] in hev},")
        print(f"                     \"relays\": {product['pid'] in relays},")
        print(f"                     \"buttons\": {product['pid'] in buttons}}},")
    print("""               None: {\t\t\t\t\t\t# Default answer for unknown product
                    "color": False,
                    "temperature": False,
                    "infrared": False,
                    "multizone": False,
                    "chain": False,
                    "matrix": False,
                    "min_kelvin": 2500,
                    "max_kelvin": 9000,
                    "hev": False,
                    "relays": False,
                    "buttons": False}
                }""")


if __name__ == "__main__":
    main()
