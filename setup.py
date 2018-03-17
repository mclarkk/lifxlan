from distutils.core import setup
#from setuptools import setup
import re

with open("lifxlan/__init__.py") as meta_file:
    metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", meta_file.read()))

setup(name='lifxlan',
      version=metadata['version'],
      description=metadata['description'],
      url=metadata['url'],
      author=metadata['author'],
      author_email=metadata['authoremail'],
      license=metadata['license'],
      packages=['lifxlan'],
      install_requires=[
        "bitstring",
        "netifaces"
        ],
      zip_safe=False,
          # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ])
