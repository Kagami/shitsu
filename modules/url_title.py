# coding: utf-8

import re
import htmlentitydefs
import modules


class Module(modules.MessageModule):

    regexp = r"(https?://[^ >]+)"
    types = ("groupchat",)
    highlight = False

    max_title_length = 150
    blacklisted_domains_rec = re.compile(
        "https?://(www\.)?(localhost|127\.0\.0\.1)")
    headers_charset_rec = re.compile("charset=([^;]{1,10})", re.I)
    meta_charset_rec = re.compile("<meta\s+[^>]*charset=([^'\";]{1,10})", re.I)
    title_rec = re.compile("<title\s*>([^<]{1,300})", re.I)

    def run(self, url):
        """Print url's title."""
        if self.blacklisted_domains_rec.match(url):
            return ""
        result = self.get_utils().get_url(url, max_page_size=5000,
                                          return_headers=True)
        if not result:
            return ""
        (data, headers) = result
        # Get page charset.
        ctype = headers.getheader("Content-Type", "")
        match = self.headers_charset_rec.search(ctype)
        if match:
            charset = match.group(1)
        else:
            match = self.meta_charset_rec.search(data)
            if match:
                charset = match.group(1)
            else:
                charset = "utf-8"
        # Decode data.
        try:
            data = data.decode(charset, "ignore")
        except Exception:
            return ""
        match = self.title_rec.search(data)
        if not match:
            return ""
        # Prettifying title.
        title = match.group(1).strip()
        title = title.replace("\t", "").replace("\n", " ")
        title = re.sub(r" {2,}", " ", title)
        title = self.unescape(title)
        if len(title) > self.max_title_length:
            title = title[:self.max_title_length] + u"…"
        return "Title: " + title

    def unescape(self, text):
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


# Test module.
if __name__ == "__main__":
    from modules.utils import Module as UtilsModule
    utils = UtilsModule(None, None)
    class DummyBot:
        def __init__(self):
            self.modules = {"utils": utils}
    module = Module(None, DummyBot())

    print "ya.ru:", module.run("http://ya.ru")
    print "youtube:", module.run("http://www.youtube.com/watch?v=ZjFIt78fCxI")
    print "rutube:", module.run("http://rutube.ru")
    print "gpl:", module.run("http://www.gnu.org/philosophy/right-to-read.ru.html")
    print "iichan:", module.run("http://iichan.ru/b/")
    print "gelbooru:", module.run("http://gelbooru.com/index.php?page=post&s=view&id=975863")
