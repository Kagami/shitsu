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
        iq = xmpp.Iq("get", xmpp.NS_DISCO_INFO, to=jid,
                     attrs={"id": utils.get_id()})
        self._bot.cl.SendAndCallForResponse(
            iq, self.got_info, {"msg": add["msg"]})
        return ""

    @utils.sandbox
    def got_info(self, cl, info, msg):
        jid = info.getFrom().getStripped()
        if info.getType() == "error":
            error = info.getTag("error")
            error_info = error.kids[0].name
            err = "%s disco info:\ngot %s error (%s)" % (
                jid, error["code"], error_info)
            self.send_message(msg, err)
            return
        iq = xmpp.Iq("get", xmpp.NS_DISCO_ITEMS, to=jid,
                     attrs={"id": utils.get_id()})
        self._bot.cl.SendAndCallForResponse(
            iq, self.parse_response, {"info": info, "msg": msg})

    @utils.sandbox
    def parse_response(self, cl, items, info, msg):
        print unicode(info)
        jid = info.getFrom().getStripped()
        info_query = info.getTag("query")
        identify = info_query.getTag("identity")
        category = identify["category"]
        name = identify["name"]
        items_list = items.getTag("query").getTags("item")
        count = len(items_list)
        if name:
            description = "\n" + name
        else:
            description = ""
        desc = ""
        if category == "conference":
            x = info_query.getTag("x", namespace=xmpp.NS_DATA)
            if x:
                desc_t = x.getTag("field", {"var": "muc#roominfo_description"})
                if desc_t:
                    desc_t = desc_t.getTag("value").getData()
                    if desc_t: desc = " (%s)" % desc_t
                count_t = x.getTag("field", {"var": "muc#roominfo_occupants"})
                if count_t: count = int(count_t.getTag("value").getData())
        if "@" in jid:
            description += "%s\ntotal: %d - " % (desc, count)
            data = map(lambda i: i["name"], items_list)
            data = ", ".join(data)
        else:
            description += "\n"
            data = map(lambda i: i["jid"], items_list)
            if len(data) > 30:
                data = data[:30] + [u"\u2026"]
            data = "\n".join(data)
        result = "%s disco info:%s%s" % (jid, description, data)
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
        self._bot.cl.SendAndCallForResponse(
            iq, self.parse_response, {"msg": add["msg"]})
        return ""

    @utils.sandbox
    def parse_response(self, cl, resp, msg):
        jid = resp.getFrom().getStripped()
        result = ""
        if resp.getType() == "result":
            if resp.kids:
                data = []
                for node in resp.kids[0].getChildren():
                    if node.name == "PHOTO":
                        data.append("<photo>")
                    else:
                        data.append(node.name.lower() + ": " +
                                    node.getCDATA())
                if data:
                    result = "\n".join(data)
                else:
                    result = "<empty>"
        if not result:
            result = "<no vcard>"
        result = jid + " vcard:\n" + result
        self.send_message(msg, result)
