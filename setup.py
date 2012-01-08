#!/usr/bin/env python

from setuptools import setup


setup(
    name="shitsu",
    version="0.1",
    license="GNU GPLv3+",
    author="Kagami Hiiragi",
    author_email="kagami@genshiken.org",
    description="tiny and flexible xmpp bot framework",
    keywords="xmpp jabber bot framework",
    url="https://github.com/Kagami/shitsu",
    packages=["shitsu", "shitsu.modules", "shitsu.utils", "shitsu.xmpp"],
    entry_points = {"console_scripts": ["shitsu = shitsu:run"]},
    package_data = {"": ["shitsu.example.cfg"]},
    classifiers=[
        "Topic :: Communications",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
)
