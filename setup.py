#!/usr/bin/env python

##################################################
# shitsu - tiny and flexible xmpp bot framework
# Copyright (C) 2008-2012 Kagami Hiiragi <kagami@genshiken.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##################################################

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
    entry_points={"console_scripts": ["shitsu = shitsu:run"]},
    package_data={"": ["shitsu.example.cfg"]},
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
