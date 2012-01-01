# coding: utf-8

import re
import codecs
import htmlentitydefs
import modules


class Module(modules.MessageModule):

    regexp = r"(https?://[^'\"\s>]+)"
    types = ("groupchat",)
    highlight = False

    max_title_length = 150
    blacklisted_domains_rec = re.compile(
        r"https?://(www\.)?(localhost|127\.0\.0\.1)")
    headers_charset_rec = re.compile(r"charset=([^;]{1,20})", re.I)
    meta_charset_rec = re.compile(
        r"<meta\s+[^>]*charset=['\"]?([^'\";\s/>]{1,20})", re.I)
    title_rec = re.compile(r"<title\s*>([^<]{1,300})", re.I)

    def run(self, url):
        """Print url's title."""
        if self.blacklisted_domains_rec.match(url):
            return ""
        result = self.get_utils().get_url(url, max_page_size=5000,
                                          return_headers=True)
        if not result:
            return ""
        (data, headers) = result
        # Get page charset. At first try headers.
        ctype = headers.getheader("Content-Type", "")
        match = self.headers_charset_rec.search(ctype)
        if match and self.is_encoding_exists(match.group(1)):
            charset = match.group(1)
        else:
            # Then check meta tag.
            match = self.meta_charset_rec.search(data)
            if match and self.is_encoding_exists(match.group(1)):
                charset = match.group(1)
            else:
                # Fallback to default.
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

    def is_encoding_exists(self, encoding):
        try:
            codecs.lookup(encoding)
        except LookupError:
            return False
        else:
            return True

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
    import sys
    from modules.utils import Module as UtilsModule
    utils = UtilsModule(None, None)
    class DummyBot:
        def __init__(self):
            self.modules = {"utils": utils}
    module = Module(None, DummyBot())

    if len(sys.argv) > 1:
        for url in sys.argv[1:]:
            print url + ": " + module.run(url)
        sys.exit()
    print "localhost:", module.run("http://localhost/")
    print "windows-1251:", module.run("http://www.yermak.com.ua/txt/pol/art_kursk.html")
    print "windpws-1251:", module.run("http://atv.odessa.ua/?t=11803")
    print "ya.ru:", module.run("http://ya.ru")
    print "youtube:", module.run("http://www.youtube.com/watch?v=ZjFIt78fCxI")
    print "gpl:", module.run("http://www.gnu.org/philosophy/right-to-read.ru.html")
    print "iichan:", module.run("http://iichan.ru/b/")
    print "gelbooru:", module.run("http://gelbooru.com/index.php?page=post&s=view&id=975863")
