from setuptools import setup

PACKAGE = "icinga2api"
NAME = "python-icinga2api"
DESCRIPTION = "python icinga2 api "
AUTHOR = "fmnisme, Tobias von der Krone"
AUTHOR_EMAIL = "fmnisme@gmail.com, tobias@vonderkrone.info"
URL = "https://github.com/tobiasvdk/python-icinga2api"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=[PACKAGE],
    zip_safe=False,
    long_description=open("README.md").read(),
)
