#!/usr/bin/env python

##################################################
# C.C. - python xmpp bot
# Copyright (C) 2008-2012 Kagami <kagami@genshiken.org>
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
os.chdir(sys.path[0])
import time
import signal
import logging
import traceback
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import xmpp
import modules.load


class CC(object):

    reload_filename_path = os.path.join("tmp", "__reload__")

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        signal.signal(signal.SIGTERM, self.sigterm_handler)

        self._done = False
        self.cl = None
        self.cfg = None
        modules.load.Load(self).run()

    def sigterm_handler(self, signum, frame):
        raise SystemExit

    def run(self):
        while not self._done:
            if os.path.isfile(self.reload_filename_path):
                os.remove(self.reload_filename_path)
                logging.info("RELOAD")
                modules.load.Load(self).run()
            try:
                if self.cl is None:
                    if self.connect():
                        logging.info("CONNECTION: bot connected")
                    else:
                        time.sleep(int(self.cfg.reconnect_time))
                else:
                    self.cl.Process(1)
            except xmpp.XMLNotWellFormed:
                logging.error("CONNECTION: reconnect (not valid XML)")
                self.cl = None
            except (KeyboardInterrupt, SystemExit):
                self.exit("EXIT: interrupted by SIGTERM")

    def connect(self):
        jid = xmpp.JID(self.cfg.jid)
        password = self.cfg.password
        debug = bool(int(self.cfg.debug))
        self.cl = xmpp.Client(jid.getDomain(), debug=debug)
        if not self.cl.connect():
            logging.error("CONNECTION: unable to connect to server")
            self.cl = None
            return
        if not self.cl.auth(jid.getNode(), password, jid.getResource()):
            logging.error("CONNECTION: unable to authorize with server")
            self.cl = None
            return
        for module in self.modules.values():
            if isinstance(module, modules.ConnectModule):
                try:
                    module.run()
                except Exception:
                    traceback.print_exc()
        self.cl.RegisterHandler("message", self.message_handler)
        self.cl.RegisterHandler("presence", self.presence_handler)
        self.cl.sendPresence()
        return True

    def exit(self, msg="EXIT: by request"):
        if self.cl is None:
            return
        for module in self.modules.values():
            if isinstance(module, modules.DisconnectModule):
                try:
                    module.run()
                except Exception:
                    traceback.print_exc()
        self.cl.sendPresence(typ="unavailable")
        self.cl.disconnect()
        logging.info(msg)
        self._done = True

    def send(self, stanza):
        if not self._done:
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
            xbody = xmpp.Node("http://www.w3.org/1999/xhtml body")
            xbody.setPayload([xhtml_body])
            xhtml.setPayload([xbody])
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
        # Allow owner's subscribe.
        if (prs.getType() == "subscribe" and
            prs.getFrom().getStripped() == self.cfg.owner_jid):
                self.send(xmpp.Presence(to=prs.getFrom(), typ="subscribed"))
                self.send(xmpp.Presence(to=prs.getFrom(), typ="subscribe"))


if __name__ == "__main__":
    CC().run()
