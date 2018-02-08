from setuptools import setup

PACKAGE = "icinga2api"
NAME = "icinga2api"
DESCRIPTION = "Python Icinga 2 API"
AUTHOR = "fmnisme, Tobias von der Krone"
AUTHOR_EMAIL = "fmnisme@gmail.com, tobias@vonderkrone.info"
URL = "https://github.com/tobiasvdk/icinga2api"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="2-Clause BSD",
    url=URL,
    packages=[PACKAGE],
    zip_safe=False,
    long_description=open("README.md").read(),
)
