#!/usr/bin/env python

from distutils.core import setup
import sys


kwds = {'long_description': open('README.rst').read()}

if sys.version_info[:2] < (2, 7):
    raise Exception('This version of bitstring needs Python 2.7 or later.')

setup(name='bitstring',
      version='3.1.7',
      description='Simple construction, analysis and modification of binary data.',
      author='Scott Griffiths',
      author_email='dr.scottgriffiths@gmail.com',
      url='https://github.com/scott-griffiths/bitstring',
      download_url='https://pypi.python.org/pypi/bitstring/',
      license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
      py_modules=['bitstring'],
      platforms='all',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      **kwds
      )

