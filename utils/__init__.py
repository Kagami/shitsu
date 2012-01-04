import datetime
import random
import socket
import urllib2


def trim(docstring):
    docstring = docstring.strip()
    return "\n".join([line.strip() for line in docstring.splitlines()])


private_hosts_re = (
    r"((www\.)?("
    r"127\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|localhost(\.localdomain)?|"
    r"192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|"
    r"172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3}"
    r"))")
default_url_timeout = 3
default_max_page_size = 1 * 1024 * 1024
request_headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 6.1; rv:9.0) "
                   "Gecko/20100101 Firefox/9.0")
}

def get_url(url, max_page_size=default_max_page_size, return_headers=False):
    request = urllib2.Request(url.encode("utf-8"), None, request_headers)
    try:
        f = urllib2.urlopen(request, timeout=default_url_timeout)
        data = f.read(max_page_size)
    except Exception:
        return ""
    else:
        if return_headers:
            return data, f.info()
        else:
            return data


def get_id():
    return "".join(map(lambda _: str(random.randint(0, 9)), xrange(10)))


# Patched version socket.create_connection from python's 2.7
# standart lib. Should work on python 2.6 and 2.7.
# Respect timeout value, do check on each cycle loop.
# Standart version can wait till `count_of_dns_records*timeout'.

def _create_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                       source_address=None):
    """Connect to *address* and return the socket object.

    Convenience function.  Connect to *address* (a 2-tuple ``(host,
    port)``) and return the socket object.  Passing the optional
    *timeout* parameter will set the timeout on the socket instance
    before attempting to connect.  If no *timeout* is supplied, the
    global default timeout setting returned by :func:`getdefaulttimeout`
    is used.  If *source_address* is set it must be a tuple of (host, port)
    for the socket to bind as a source address before making the connection.
    An host of '' or port 0 tells the OS to use the default.
    """

    host, port = address
    err = None
    if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
        start = datetime.datetime.now()
        delta = datetime.timedelta(seconds=timeout)
        check_timeout = True
    else:
        check_timeout = False
    for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                sock.settimeout(timeout)
            if source_address:
                sock.bind(source_address)
            sock.connect(sa)
            return sock

        except socket.error as _:
            err = _
            if sock is not None:
                sock.close()
        if check_timeout and datetime.datetime.now() - start >= delta:
            break

    if err is not None:
        raise err
    else:
        raise socket.error("getaddrinfo returns an empty list")

socket.create_connection = _create_connection
