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

import socket
import subprocess
from shitsu import modules
from shitsu import utils
reload(utils)


class Port(modules.MessageModule):

    args = (2,)
    allow_conf_private = False
    thread_safe = False

    def run(self, host, port):
        """<host> <port>
        Check host's port.
        """
        host = utils.fix_host(host)
        if not host:
            return
        try:
            port = int(port)
        except ValueError:
            return
        if not 0 < port < 65536:
            return
        try:
            sock = socket.create_connection((host, port), timeout=3)
        except socket.error:
            return "port %d closed" % port
        else:
            sock.close()
            return "port %d open" % port


class Nmap(modules.MessageModule):

    args = (1,)
    allow_conf_private = False
    thread_safe = False

    nmap_args = "nmap -PN -T4 --host-timeout 10s".split()

    def run(self, host):
        """<host>
        Scan host with nmap.
        """
        host = utils.fix_host(host)
        if not host:
            return
        args = self.nmap_args + [host]
        try:
            popen = subprocess.Popen(
                args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            stdout = popen.communicate()[0]
        except OSError:
            return "Nmap run failed. Has it installed?"
        lines = stdout.splitlines()[3:]
        return "\n".join(lines)
