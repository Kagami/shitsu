# coding: utf-8

import re
import codecs
import modules
import utils
reload(utils)


class Urltitle(modules.MessageModule):

    regexp = r"(https?://[^'\"\s>]{1,500})"
    types = ("groupchat",)
    highlight = False

    max_title_length = 150
    headers_charset_rec = re.compile(r"charset=([^;]{1,20})", re.I)
    meta_charset_rec = re.compile(
        r"<meta\s+[^>]*charset=['\"]?([^'\";\s/>]{1,20})", re.I)
    title_rec = re.compile(r"<title\s*>([^<]{1,300})", re.I)

    def run(self, url):
        """Get url's title."""
        result = utils.get_url(url, max_page_size=5000, return_headers=True,
                               forbid_private=True)
        if not result:
            return ""
        (data, headers) = result
        # Get page charset. At first try headers.
        ctype = headers.getheader("Content-Type", "")
        if not ctype.startswith("text/html"):
            return ""
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
        title = utils.unescape(title)
        if len(title) > self.max_title_length:
            title = title[:self.max_title_length] + u"\u2026"
        return "Title: " + title

    def is_encoding_exists(self, encoding):
        try:
            codecs.lookup(encoding)
        except LookupError:
            return False
        else:
            return True



# Test module.
if __name__ == "__main__":
    import sys
    module = Urltitle(None)

    if len(sys.argv) > 1:
        for url in sys.argv[1:]:
            print url + ": " + module.run(url)
        sys.exit()
    print "localhost:", module.run("http://localhost/")
    print u"тохо.рф:", module.run(u"http://тохо.рф/")
    print "windows-1251:", module.run("http://www.yermak.com.ua/txt/pol/art_kursk.html")
    print "windpws-1251:", module.run("http://atv.odessa.ua/?t=11803")
    print "ya.ru:", module.run("http://ya.ru/")
    print "youtube:", module.run("http://www.youtube.com/watch?v=ZjFIt78fCxI")
    print "gpl:", module.run("http://www.gnu.org/philosophy/right-to-read.ru.html")
    print "iichan:", module.run("http://iichan.ru/b/")
    print "gelbooru:", module.run("http://gelbooru.com/index.php?page=post&s=view&id=975863")
    print "https://ya.ru:", module.run("https://ya.ru/")
