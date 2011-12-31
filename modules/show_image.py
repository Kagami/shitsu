import xmpp
import modules


class Module(modules.MessageModule):

    name = "s"
    args = (1,)

    def run(self, img_url):
        """<img_url>
        Show img via xhtml-im.
        http://xmpp.org/extensions/xep-0071.html#profile-image
        """
        img = xmpp.Node("img", attrs={"alt": "img", "src": img_url})
        return "<enable xhtml-im to see image>", img
