import re
import urllib2
import modules


class Module(modules.BaseModule):

    def trim(self, docstring):
        docstring = docstring.strip()
        return u"\n".join([line.strip() for line in docstring.splitlines()])

    url_timeout = 3
    request_headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 5.1; rv:8.0) "
                       "Gecko/20100101 Firefox/8.0")
    }
    def get_url(self, url):
        request = urllib2.Request(
            url.encode("utf-8"), None, self.request_headers)
        try:
            return urllib2.urlopen(request, None, self.url_timeout).read()
        except Exception:
            return ""
