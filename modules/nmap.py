import re
import socket
import subprocess
import modules
import utils
reload(utils)


host_rec = re.compile(r"^([-a-z0-9]{1,63}\.)+[a-z0-9]{1,63}$")
private_hosts_rec = re.compile(r"^%s$" % utils.private_hosts_re)

def is_host_ok(host):
    if not host_rec.match(host):
       return False
    if private_hosts_rec.match(host):
        return False
    if len(host) > 255:
        return False
    return True


class Port(modules.MessageModule):

    args = (2,)

    def run(self, host, port):
        """<host> <port>
        Check host's port.
        """
        if not is_host_ok(host):
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

    nmap_args = "nmap -PN -F -T4 --host-timeout 5s".split()

    def run(self, host):
        """<host>
        Scan host with nmap.
        """
        if not is_host_ok(host):
            return
        args = self.nmap_args + [host]
        try:
            popen = subprocess.Popen(
                args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            stdout = popen.communicate()[0]
        except OSError:
            return "Nmap run failed. Does it installed?"
        lines = stdout.splitlines()[3:]
        return "\n".join(lines)
