from xml.sax.saxutils import escape
import xmpp


def main(bot, args):
    """show <url>\nShow img by url."""

    if len(args) == 1:
        return args[0], getImgXML(args[0])


def getImgXML(img_url):
    img_url = escape(img_url.replace('"', '').replace('\'', ''))

    node = xmpp.Node(xmpp.NS_XHTML_IM + ' html')
    body = xmpp.Node('http://www.w3.org/1999/xhtml body')
    body.addChild('img', attrs={'alt': 'img', 'src': img_url})
    node.setPayload([body])
    return unicode(node)


if __name__ == '__main__':
    print main(None, ["http://nya.ru/1.jpg"])
