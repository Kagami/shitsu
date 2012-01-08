import re
import random
import urllib2
import urlparse
import traceback
import htmlentitydefs
from shitsu.utils import fix_socket
reload(fix_socket)


def trim(docstring):
    docstring = docstring.strip()
    return "\n".join([line.strip() for line in docstring.splitlines()])


def sandbox(fn):
    def new(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except Exception:
            traceback.print_exc()
    return new


host_rec = re.compile(r"^([-A-Za-z0-9]{1,63}\.)*[-A-Za-z0-9]{1,63}\.?$")
private_hosts_rec = re.compile(
    r"^("
    r"127\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|localhost(\.localdomain)?|"
    r"192\.168\.[0-9]{1,3}\.[0-9]{1,3}|10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|"
    r"172\.(1[6-9]|2[0-9]|3[0-1])\.[0-9]{1,3}\.[0-9]{1,3}"
    r")$")

def fix_host(host, forbid_private=False):
    """Check validness of hostname and fix idna hosts.
    Optionally forbid private hosts.
    """
    if len(host) > 255:
        return
    try:
        host = host.encode("idna")
    except UnicodeError:
        return
    if not host_rec.match(host):
        return
    if forbid_private and private_hosts_rec.match(host):
        return
    return host


def fix_url(url, forbid_private=False):
    """Check and fix url's hostname via fix_host."""
    p = urlparse.urlsplit(url)
    userpass, at, hostport = p.netloc.partition("@")
    if not at: userpass, hostport = "", userpass
    host, colon, port = hostport.partition(":")
    host = fix_host(p.hostname, forbid_private)
    if not host:
        return
    netloc = "".join([userpass, at, host, colon, port])
    p2 = urlparse.urlunsplit((p.scheme, netloc, p.path, p.query, p.fragment))
    return p2.encode("utf-8")


default_url_timeout = 4
default_max_page_size = 1 * 1024 * 1024
request_headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 6.1; rv:9.0) "
                   "Gecko/20100101 Firefox/9.0")
}

def get_url(url, max_page_size=default_max_page_size, return_headers=False,
            timeout=default_url_timeout, forbid_private=False):
    url = fix_url(url, forbid_private)
    if not url:
        return ""
    request = urllib2.Request(url, None, request_headers)
    try:
        f = urllib2.urlopen(request, timeout=timeout)
        data = f.read(max_page_size)
    except Exception:
        return ""
    else:
        if return_headers:
            return data, f.info()
        else:
            return data


def unescape(text):
    """Removes HTML or XML character references and
    entities from a text string.
    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.
    Source: http://effbot.org/zone/re-sub.htm#unescape-html
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def get_id():
    return "".join(map(lambda _: str(random.randint(0, 9)), xrange(10)))
