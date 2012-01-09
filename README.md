## shitsu - tiny and flexible xmpp bot framework

### Proposal

Obviously there are a huge bunch of various jabber bots available  
but each that I had seen offer a-lot-of-commands rather than cool API.  
shitsu aims to be pythonic, pep8-compatible, clean and simple framework  
with the main purpose to make it easy to write a module.

### Installation

(There are a lot of methods - setuptools, distribute, pip, virtualenv,  
etc. be we will examine the simpliest one.)

* **Windows**
    1. Get the latest python 2.x from <http://python.org/download/> and install it.
    2. Click the zip button at the top of this page, save and unpack.
    3. Go to the shitsu/shitsu directory and copy the file **shitsu.example.cfg**  
    to **shitsu.cfg** - there will be your config.

* **Linux (Debian example)**
    1. `sudo apt-get install python-pip git-core`
    2. `sudo pip install git+https://github.com/Kagami/shitsu.git`
    3. `shitsu` and answer **y** - shitsu will create stub config in your home folder.

### Configuration

**jid**, **password** and **owner\_jid** options are required.  
Other options meant to be self-documenting - read the comments.

### Usage

On Windows just double-click `run_without_install.py`  
On Linux: `shitsu`  
Additional options can be obtained via **--help** option:

    % shitsu --help
    Usage: shitsu [options]

    Options:
      -h, --help    show this help message and exit
      -d, --debug   print additional debug info
      -r, --reload  reload shitsu's config and modules on the fly

### Bot usage

To start simply send `%help` command to bot from owner's jid.

### Writing modules

See the [wiki page](https://github.com/Kagami/shitsu/wiki/API).

### License

shitsu licensed under the GNU GPLv3+. See the copyright notice below.  
Note that shitsu included:

* xmpppy library by Alexey Nezhdanov <http://xmpppy.sourceforge.net/>  
(GNU GPLv2+) with some minor patches; shitsu.xmpp package
* BeautifulSoup by Leonard Richardson  
<http://www.crummy.com/software/BeautifulSoup/> (BSD-like);  
shitsu.utils.BeautifulSoup
* some code in shitsu.utils package under the BSD-like license  

Fortunately them are all GPL-compatible.

    shitsu - tiny and flexible xmpp bot framework
    Copyright (C) 2008-2012 Kagami Hiiragi <kagami@genshiken.org>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
