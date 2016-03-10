from setuptools import setup, find_packages
import os
import sys


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '0.0.1'
AUTHOR = 'Binyamin Sharet'
EMAIL = 's.binyamin@gmail.com'
URL = 'https://github.com/BinyaminSharet/Mtp.py'
DESCRIPTION = read('README.rst')


setup(
    name='pymtpdevice',
    version=VERSION,
    description='MTP device stack',
    long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(),
    install_requires=['docopt'],
    keywords='fuzz framework sulley kitty',
)
