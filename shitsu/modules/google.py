##################################################
# shitsu - tiny and flexible xmpp bot framework
# Copyright (C) 2008-2012 Kagami Hiiragi <kagami@genshiken.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##################################################

import re
import json
import urllib
from shitsu.xmpp.simplexml import XMLescape
from shitsu import modules
from shitsu import utils
reload(utils)


class Google(modules.MessageModule):

    raw_query = True

    def run(self, query):
        """<query>
        Google search. Return the first result.
        """
        if not query:
            return
        query = urllib.urlencode({
            "v": "1.0",
            "q": query.encode("utf-8"),
        })
        url = "http://ajax.googleapis.com/ajax/services/search/web?" + query
        data = utils.get_url(url)
        if not data:
            return "can't get data"
        data = json.loads(data)
        if data["responseStatus"] != 200:
            return "google returned %d error" % data["responseStatus"]
        jresults = data["responseData"]["results"]
        if not jresults:
            return "no results found"
        jres = jresults[0]
        title = jres["titleNoFormatting"]
        content_text = jres["content"].replace("   ", "\n")
        content_text = content_text.replace("<b>", "").replace("</b>", "")
        content_xhtml = jres["content"].replace("   ", "<br />")
        content_xhtml = re.sub(
            r"<b>(.*?)</b>",
            "<span style='font-weight: bold;'>\g<1></span>",
            content_xhtml)
        url = urllib.unquote(str(jres["unescapedUrl"])).decode("utf-8")
        result = "%s\n%s\n%s" % (title, content_text, url)
        url = XMLescape(url)
        result_xhtml = "%s<br />%s<br /><a href='%s'>%s</a>" % (
            title, content_xhtml, url, url)
        return result, result_xhtml
