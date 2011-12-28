from xmpp.simplexml import XMLescape
import xmpp


def main(bot, args):
    """show <url>
    Show img via xhtml-im.
    http://xmpp.org/extensions/xep-0071.html#profile-image
    """
    if len(args) == 1:
        img_url = XMLescape(args[0])
        xml = xmpp.Node('img', attrs={'alt': 'img', 'src': img_url})
        return args[0], xml
