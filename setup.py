from setuptools import setup

setup(name='lifxlan',
      version='0.2.3',
      description='API for local communication with LIFX devices over a LAN.',
      url='http://github.com/mclarkk/lifxlan',
      author='Meghan Clark',
      author_email='mclarkk@umich.edu',
      license='MIT',
      packages=['lifxlan'],
      install_requires=[
        "bitstring",
	  ],
      zip_safe=False)
