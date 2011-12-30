# coding: utf-8

import re
# TODO: Use python's standart htmlparser.
from lxml import etree
import modules


class Module(modules.MessageModule):

    regexp = r"(https?://[^ >]+)"
    types = ("groupchat",)
    highlight = False

    max_title_length = 150
    blacklisted_domains_rec = re.compile(
        "https?://(www\.)?(localhost|127\.0\.0\.1)")

    def run(self, url):
        """Print url's title."""
        if self.blacklisted_domains_rec.match(url) is not None:
            return ""
        data = self.get_utils().get_url(url)
        if not data:
            return ""
        # TODO: Graceful decoding.
        try:
            data = data.decode("utf-8")
        except Exception:
            try:
                data = data.decode("cp1251")
            except Exception:
                pass
        try:
            title = etree.HTML(data).find(".//title").text.strip()
        except Exception:
            return ""
        title = title.replace("\t", "").replace("\n", " ")
        title = re.sub(r" {2,}", " ", title)
        if len(title) > self.max_title_length:
            title = title[:self.max_title_length] + u"…"
        return "Title: " + title
