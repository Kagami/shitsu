import re
import json
import urllib
from xmpp.simplexml import XMLescape
import modules
import utils
reload(utils)


class G(modules.MessageModule):

    raw_query = True

    # TODO: Use new API!
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
        content_text = jres["content"].replace("   ", "\n")
        content_text = content_text.replace("<b>", "").replace("</b>", "")
        content_xhtml = jres["content"].replace("   ", "<br />")
        content_xhtml = re.sub(
            r"<b>(.*?)</b>",
            "<span style='font-weight: bold;'>\g<1></span>",
            content_xhtml)
        url = urllib.unquote(str(jres["unescapedUrl"])).decode("utf-8")
        result = "%s\n%s\n%s" % (jres["titleNoFormatting"], content_text, url)
        url = XMLescape(url)
        result_xhtml = "%s<br />%s<br /><a href='%s'>%s</a>" % (
            jres["titleNoFormatting"], content_xhtml, url, url)
        return result, result_xhtml
