import os
from setuptools import setup, find_packages

PACKAGE = "icinga2api"
NAME = "python-icinga2api"
DESCRIPTION = "python icinga2 api "
AUTHOR = "fmnisme, Tobias von der Krone"
AUTHOR_EMAIL = "fmnisme@gmail.com, tobias@vonderkrone.info"
URL = "https://github.com/tobiasvdk/python-icinga2api"
VERSION = __import__(PACKAGE).__version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=find_packages(),
    zip_safe=False,
    long_description=read('README.md'),
)
