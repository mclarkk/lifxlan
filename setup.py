from distutils.core import setup
# from setuptools import setup
import re

with open("lifxlan3/__init__.py") as meta_file:
    metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", meta_file.read()))
packages = 'lifxlan3 lifxlan3.devices lifxlan3.network lifxlan3.routines lifxlan3.routines.light lifxlan3.routines.tile'.split()
setup(name='lifxlan3',
      version=metadata['version'],
      description=metadata['description'],
      url=metadata['url'],
      author=metadata['author'],
      author_email=metadata['authoremail'],
      license=metadata['license'],
      packages=packages,
      package_dir={p: p.replace('.', '/') for p in packages},
      install_requires=[
          'bitstring',
          'netifaces',
          'getch',
          'arrow', 'click', 'sty', 'Pillow'
      ],
      zip_safe=False,
      include_package_data=True,
      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3.6'
          'Programming Language :: Python :: 3.7'
      ])
