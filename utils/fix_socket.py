import socket
import datetime


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
