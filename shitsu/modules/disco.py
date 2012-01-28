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

from shitsu import xmpp
from shitsu import modules
from shitsu import utils
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
            err = "%s disco:\ngot %s error (%s)" % (
                jid, error["code"], error_info)
            self.send_message(msg, err)
            return
        iq = xmpp.Iq("get", xmpp.NS_DISCO_ITEMS, to=jid,
                     attrs={"id": utils.get_id()})
        self._bot.cl.SendAndCallForResponse(
            iq, self.parse_response, {"info": info, "msg": msg})

    @utils.sandbox
    def parse_response(self, cl, items, info, msg):
        jid = info.getFrom().getStripped()
        info_query = info.getTag("query")
        for i in info_query.getTags("identity"):
            if i["name"]:
                name = i["name"]
                break
        items_list = items.getTag("query").getTags("item")
        if "@" in jid:
            desc = ""
            count = len(items_list)
            x = info_query.getTag("x", namespace=xmpp.NS_DATA)
            if x:
                desc_t = x.getTag("field", {"var": "muc#roominfo_description"})
                if desc_t:
                    desc_t = desc_t.getTag("value").getData()
                    if desc_t: desc = " (%s)" % desc_t
                count_t = x.getTag("field", {"var": "muc#roominfo_occupants"})
                if count_t:
                    count = int(count_t.getTag("value").getData())
            features = []
            if info_query.getTag("feature", {"var": "muc_membersonly"}):
                features.append("membersonly")
            if info_query.getTag("feature", {"var": "muc_passwordprotected"}):
                features.append("password")
            if features:
                features = " [%s]" % (", ".join(features))
            else:
                features = ""
            description = "%s%s\ntotal: %d" % (desc, features, count)
            if items_list:
                data = map(lambda i: i["name"], items_list)
                data = description + " - " + ", ".join(data)
            else:
                data = description
        else:
            data = "\n" + "\n".join(map(lambda i: i["jid"], items_list))
        result = name + data
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
        if resp.getType() == "error":
            error = resp.getTag("error")
            error_info = error.kids[0].name
            result = "%s vcard:\ngot %s error (%s)" % (
                jid, error["code"], error_info)
        else:
            if resp.kids:
                data = []
                for node in resp.kids[0].getChildren():
                    if node.name == "PHOTO":
                        data.append("<photo>")
                    else:
                        cdata = node.getCDATA()
                        if cdata:
                            data.append(node.name.lower() + ": " + cdata)
                if data:
                    result = "\n" + "\n".join(data)
                else:
                    result = "empty"
            else:
                result = "no vcard"
        self.send_message(msg, result)
