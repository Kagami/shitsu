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
