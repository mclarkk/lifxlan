__author__ = 'acushner'

import json

import pkgutil
from contextlib import suppress


def _read_products():
    products = pkgutil.get_data('lifxlan3', 'product_data/products.json')
    products = json.loads(products.decode())
    return products[0]['products']


def _product_map(products):
    return {p['pid']: p['name'] for p in products}


def _features_map(products):
    keys = 'color', 'temperature', 'infrared', 'multizone', 'chain'

    def _transform_features(feat):
        res = {k: feat.get(k, False) for k in keys}
        mn = mx = None
        with suppress(Exception):
            mn, mx = feat['temperature_range']
            res['temperature'] = True
        res['min_kelvin'], res['max_kelvin'] = mn, mx
        return res

    return {p['pid']: _transform_features(p['features']) for p in products}


_p = _read_products()
product_map = _product_map(_p)
light_products = list(product_map)
features_map = _features_map(_p)


def __main():
    print(features_map[1])
    print(_p[0])
    pass


if __name__ == '__main__':
    __main()
