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

import os
import sys
import time
import signal
import logging
import traceback
import xml.parsers.expat
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from shitsu import xmpp
from shitsu import modules
from shitsu.modules import core


class ShiTsu(object):

    def __init__(self, options):
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        signal.signal(signal.SIGTERM, self.sigterm_handler)

        self.options = options
        self._done = False
        self.cl = None
        self.cfg = None
        self.confs = {}
        self.threads_num = 0
        core.Load(self).run()

    def sigterm_handler(self, signum, frame):
        raise SystemExit

    def run(self):
        while not self._done:
            if os.path.isfile(self.options.reload_path):
                os.remove(self.options.reload_path)
                logging.info("RELOAD")
                core.Load(self).run()
            try:
                if not self.cl:
                    if self.connect():
                        logging.info("CONNECTION: bot connected")
                    else:
                        timeout = int(self.cfg.get("reconnect_time", 10))
                        logging.info(
                            "CONNECTION: sleep for %d seconds "
                            "before reconnect attempt" % timeout)
                        time.sleep(timeout)
                else:
                    self.cl.Process(1)
            except xmpp.XMLNotWellFormed:
                logging.error("CONNECTION: reconnect (non-valid XML)")
                self.cl = None
            except (KeyboardInterrupt, SystemExit):
                self.exit("EXIT: interrupted by SIGTERM")
        if self.cl:
            self.cl.disconnect()

    def connect(self):
        jid = xmpp.JID(self.cfg.jid)
        password = self.cfg.password
        cl = xmpp.Client(jid.getDomain(), debug=self.options.debug)
        if not cl.connect():
            logging.error(
                "CONNECTION: unable to connect to %s" % jid.getDomain())
            return
        if not cl.auth(jid.getNode(), password, jid.getResource()):
            logging.error("CONNECTION: unable to authorize (check password)")
            return
        self.cl = cl
        self.cl.sendPresence()
        for module in self.modules.values():
            if isinstance(module, modules.ConnectModule):
                try:
                    module.run()
                except Exception:
                    traceback.print_exc()
        self.cl.RegisterHandler("message", self.message_handler, "chat")
        self.cl.RegisterHandler("message", self.message_handler, "groupchat")
        self.cl.RegisterHandler("presence", self.presence_handler)
        self.cl.RegisterHandler("iq", self.iq_handler, "get")
        return True

    def exit(self, msg="EXIT: by request"):
        if self.cl:
            for module in self.modules.values():
                if isinstance(module, modules.DisconnectModule):
                    try:
                        module.run()
                    except Exception:
                        traceback.print_exc()
            self.cl.sendPresence(typ="unavailable")
        logging.info(msg)
        self._done = True

    def send(self, stanza):
        if self.cl and not self._done:
            self.cl.send(stanza)

    def send_join(self, conf_jid, password=None):
        x = xmpp.Node(xmpp.NS_MUC + " x")
        if password:
            x.addChild("password", payload=password)
        x.addChild("history", attrs={"maxstanzas": "0"})
        self.send(xmpp.Presence(to=conf_jid, payload=[x]))

    def send_leave(self, conf_jid):
        self.send(xmpp.Presence(to=conf_jid, typ="unavailable"))

    def send_message(self, to, type_, body, xhtml_body=None):
        msg = xmpp.Message(to=to, typ=type_, body=body)
        if xhtml_body:
            xhtml = xmpp.Node(xmpp.NS_XHTML_IM + " html")
            body = xhtml.addChild("http://www.w3.org/1999/xhtml body")
            body.setPayload([xhtml_body])
            xhtml_s = unicode(xhtml)
            try:
                xmpp.simplexml.XML2Node(xhtml_s.encode("utf-8"))
            except xml.parsers.expat.ExpatError as e:
                logging.error("PARSER: %s (%s)" % (e, xhtml_s))
            else:
                msg.addChild(node=xhtml)
        self.send(msg)

    def message_handler(self, cl, msg):
        for module in self.modules.values():
            if isinstance(module, modules.MessageModule):
                try:
                    module.handle(msg)
                except Exception:
                    traceback.print_exc()

    def presence_handler(self, cl, prs):
        # TODO: PresenceModule
        from_ = prs.getFrom()
        if prs.getType() == "subscribe":
            if from_ == self.cfg.owner_jid:
                # Allow owner's subscribe.
                self.send(xmpp.Presence(to=from_, typ="subscribed"))
                self.send(xmpp.Presence(to=from_, typ="subscribe"))
            else:
                self.send(xmpp.Presence(to=from_, typ="unsubscribed"))

    def iq_handler(self, cl, iq):
        if iq.getQueryNS() == xmpp.NS_VERSION:
            # Send bot's version.
            iq_to = xmpp.Iq("result", xmpp.NS_VERSION, to=iq.getFrom())
            iq_to.setID(iq.getID())
            query = iq_to.getTag("query")
            query.NT.name = "shitsu"
            query.NT.version = self.options.version
            query.NT.os = "python " + ".".join(map(str, sys.version_info[:3]))
            self.send(iq_to)
            raise xmpp.NodeProcessed
