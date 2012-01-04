import re
import datetime
from BeautifulSoup import BeautifulSoup
import modules
import utils
reload(utils)


class Animecal(modules.MessageModule):

    args = (0, 1, 2, 3)

    def run(self, day=None, month=None, year=None):
        """[day [month [yeah]]]
        Show anime list airing today (timezone UTC+9) or at specified date.
        Source: http://animecalendar.net/
        """
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        try:
            if day: now = now.replace(day=int(day))
            if month: now = now.replace(month=int(month))
            if year: now = now.replace(year=int(year))
        except Exception:
            return
        url = "http://animecalendar.net/%d/%d/%d" % (
            now.year, now.month, now.day)
        data = utils.get_url(url)
        if not data:
            return "can't get data"

        if day:
            info = "Anime for %02d.%02d.%d" % (now.day, now.month, now.year)
            time_str = ""
        else:
            info = "Anime for today"
            time_str = " now: %02d:%02d (UTC+9)" % (now.hour, now.minute)
        anime_list = ["%s <%s>%s" % (info, url, time_str)]
        anime_list_xhtml = [
            "%s &lt;<a href='%s'>%s</a>&gt;%s" % (info, url, url, time_str)
        ]
        soup = BeautifulSoup(data)
        for div in soup.findAll("div", {"class": "ep_box"}):
            anime = div.h3.a.string.strip()
            ep = div.small.string.replace("\t", "").replace("\n", "")
            anime_list.append("%s (%s)" % (anime, ep))

            line = "%s <span style='font-style: italic;'>(%s)</span>" % (
                anime, ep)
            if not day:
                (h, m) = re.search("at (\d{2}):(\d{2})", ep).groups()
                start_time = now.replace(hour=int(h), minute=int(m))
                delta = (now - start_time).seconds / 60
                if delta > 0 and delta < 30:
                    line = "<span style='font-weight: bold;'>%s</span>" % line
            anime_list_xhtml.append(line)
        if len(anime_list) == 1:
            s = "No anime :((("
            anime_list.append(s)
            anime_list_xhtml.append(s)
        return "\n".join(anime_list), "<br />".join(anime_list_xhtml)


if __name__ == "__main__":
    (text, xhtml) = Animecal(None).run()
    print text
    print "==="
    print xhtml
