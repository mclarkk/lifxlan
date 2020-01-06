#!/usr/bin/env python3
# This python 3.6+ script is a quick products.py file generator

import json
import re
import http.client
import sys

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

    i = 0
    for product in mapdata:
        i += 1
        if i < num_products:
            print(f"               {product['pid']}: \"{product['name']}\",")
        else:
            print(f"               {product['pid']}: \"{product['name']}\"")

    print("              }") 
    print("")
    print("# Identifies which products are lights.")
    print("# Currently all LIFX products that speak the LAN protocol are lights.")
    print("# However, the protocol was written to allow addition of other kinds")
    print("# of devices, so it's important to be able to differentiate.")

    products = []
    for product in mapdata:
        products.append(product['pid'])

    lightproducts = ', '.join(map(str, products))
    print(f"light_products = [{lightproducts}]")
    print("")

    print("features_map = {") 
    i = 0
    for product in mapdata:
        i += 1
        if product['features']['temperature_range'][0] != product['features']['temperature_range'][1]:
            temp = True
        else:
            temp = False
        if re.search('tile', product['name'], re.IGNORECASE):
            chain = True
        else:
            chain = False

        print(f"                {product['pid']}: {{\"color\": {product['features']['color']},")
        print(f"                     \"temperature\": {temp},")
        print(f"                     \"infrared\": {product['features']['infrared']},")
        print(f"                     \"multizone\": {product['features']['multizone']},")
        print(f"                     \"chain\": {chain},")
        print(f"                     \"min_kelvin\": {product['features']['temperature_range'][0]},")

        if i < num_products:
            print(f"                     \"max_kelvin\": {product['features']['temperature_range'][1]}}},")
        else:
            print(f"                     \"max_kelvin\": {product['features']['temperature_range'][1]}}}")

    print("               }") 
        

if __name__ == "__main__":
    main()
