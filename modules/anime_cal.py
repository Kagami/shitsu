import re
import datetime
# TODO: Use python's standart htmlparser.
from lxml import etree
import modules


class Module(modules.MessageModule):

    name = "a"
    args = (0,)

    def run(self):
        """anime
        Show anime list airing today (timezone UTC+9).
        Source: http://animecalendar.net/
        """
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        url = "http://animecalendar.net/%d/%d/%d" % (
            now.year, now.month, now.day)
        data = self.get_utils().get_url(url)
        if not data:
            return "can't get data"

        tree = etree.HTML(data)
        time_str = " ; now: %02d:%02d (UTC+9)" % (now.hour, now.minute)
        anime_list = ["Anime for today from " + url + time_str]
        anime_list_xhtml = [
            "Anime for today from <a href='%s'>%s</a>%s" % (url, url, time_str)
        ]
        for div in tree.findall(".//div[@class='ep_box']"):
            anime = div.find("h3").find("a").text.strip()
            ep = div.find("small").text.replace("\t", "").replace("\n", "")
            anime_list.append("%s (%s)" % (anime, ep))

            line = "%s <span style='font-style: italic;'>(%s)</span>" % (
                anime, ep)
            (h, m) = re.search("at (\d{2}):(\d{2})", ep).groups()
            start_time = now.replace(hour=int(h), minute=int(m))
            delta = (now - start_time).seconds / 60
            if delta > 0 and delta < 30:
                line = "<span style='font-weight: bold;'>%s</span>" % line
            anime_list_xhtml.append(line)
        if len(anime_list) == 1:
            s = "No anime for today :((("
            anime_list.append(s)
            anime_list_xhtml.append(s)
        return u"\n".join(anime_list), u"<br />".join(anime_list_xhtml)


if __name__ == "__main__":
    (text, xhtml) = Module(None, None).run()
    print text
    print "==="
    print xhtml
