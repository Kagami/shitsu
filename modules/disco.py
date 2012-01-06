import xmpp
import modules
import utils
reload(utils)


class Disco(modules.MessageModule):

    args = (1,)
    additional_args = True

    def run(self, jid, add):
        """<jid>
        Print jid's disco info.
        See http://xmpp.org/extensions/xep-0030.html
        """
        jid = xmpp.JID(jid).getStripped()
        iq = xmpp.Iq("get", xmpp.NS_DISCO_ITEMS, to=jid,
                     attrs={"id": utils.get_id()})
        self._bot.cl.SendAndCallForResponse(iq, self.parse_response,
                                            {"msg": add["msg"]})
        return ""

    @utils.sandbox
    def parse_response(self, cl, resp, msg):
        items = resp.getTag("query").getTags("item")
        if items:
            jid = resp.getFrom().getStripped()
            is_conf = True if "@" in jid else False
            items_info = []
            for item in items:
                if is_conf:
                    items_info.append(item["name"])
                else:
                    items_info.append(item["jid"])
            if is_conf:
                result = "Total: %d\n%s" %(
                    len(items), ", ".join(items_info))
            else:
                if len(items_info) > 30:
                    items_info = items_info[:30] + [u"\u2026"]
                result = "\n" + "\n".join(items_info)
        else:
            result = "no info"
        self.send_message(msg, result)


class Vcard(modules.MessageModule):

    args = (1,)
    additional_args = True

    def run(self, jid, add):
        """<jid>
        Print jid's vcard info.
        See http://xmpp.org/extensions/xep-0054.html
        """
        jid = xmpp.JID(jid).getStripped()
        iq = xmpp.Iq("get", to=jid, attrs={"id": utils.get_id()})
        iq.addChild(xmpp.NS_VCARD + " vCard")
        self._bot.cl.SendAndCallForResponse(iq, self.parse_response,
                                            {"msg": add["msg"]})
        return ""

    @utils.sandbox
    def parse_response(self, cl, resp, msg):
        result = ""
        if resp.getType() == "result":
            vcard = resp.getPayload()
            if vcard:
                data = []
                for node in vcard[0].getPayload():
                    if type(node) is not xmpp.Node:
                        continue
                    if node.name == "PHOTO":
                        data.append("<photo>")
                    else:
                        data.append(node.name.lower() + ": " + node.getCDATA())
                if data:
                    result = "\n".join(data)
                else:
                    result = "<empty>"
        if not result:
            result = "<no vcard>"
        result = "\n" + result
        self.send_message(msg, result)
