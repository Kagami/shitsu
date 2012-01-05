import socket
import subprocess
import modules
import utils
reload(utils)


class Port(modules.MessageModule):

    args = (2,)
    types = ("groupchat",)

    def run(self, host, port):
        """<host> <port>
        Check host's port.
        """
        host = utils.fix_host(host, forbid_private=True)
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
    types = ("groupchat",)

    nmap_args = "nmap -PN -F -T4 --host-timeout 5s".split()

    def run(self, host):
        """<host>
        Scan host with nmap.
        """
        host = utils.fix_host(host, forbid_private=True)
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


# Test module.
if __name__ == "__main__":
    module = Nmap(None)

    print module.run("127.0.0.1")
    print module.run("127.0.3.1")
    print module.run("192.168.1.5")
    print module.run("www.localhost")
    print module.run("172.16.1.1")
