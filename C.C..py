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
import time
import signal
import logging
import traceback
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
try:
    import xmpp
except ImportError:
    path = os.path.join(os.path.dirname(__file__), "lib")
    sys.path.insert(0, path)
    import xmpp
import modules.load
import config


class CC(object):

    RECONNECT_TIME = 30

    def __init__(self, user, rooms, owner):
        self._done = False
        self.cl = None
        self.jid = xmpp.JID(user[0])
        self.password = user[1]
        self.res = user[2]
        self.rooms = list(rooms)
        self.owner = owner

        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, signum, frame):
        raise SystemExit

    def run(self):
        modules.load.Module("load", self).run()
        while not self._done:
            try:
                if self.cl is None:
                    if self.connect():
                        logging.info("CONNECTION: bot connected")
                    else:
                        time.sleep(self.RECONNECT_TIME)
                else:
                    self.cl.Process(1)
            except xmpp.protocol.XMLNotWellFormed:
                logging.error("CONNECTION: reconnect (not valid XML)")
                self.cl = None
            except (KeyboardInterrupt, SystemExit):
                self.exit("EXIT: interrupted by SIGTERM")

    def connect(self):
        self.cl = xmpp.Client(self.jid.getDomain(), debug = [])
        if not self.cl.connect():
            logging.error("CONNECTION: unable to connect to server")
            return
        if not self.cl.auth(self.jid.getNode(), self.password, self.res):
            logging.error("CONNECTION: unable to authorize with server")
            return
        for room in self.rooms:
            self.send_join(*room)
        self.cl.RegisterHandler("message", self.message_handler)
        self.cl.RegisterHandler("presence", self.presence_handler)
        self.cl.sendPresence()
        return True

    def exit(self, msg="exit"):
        if self.cl is None:
            return
        for room in self.rooms:
            self.leave(room)
        try:
            self.cl.disconnect()
        except AttributeError:
            # TODO: Why does this happen on disconnect?
            # %%C.O.: xmpppy is crap%%
            pass
        logging.info(msg)
        self._done = True

    def send(self, stanza):
        if not self._done:
            self.cl.send(stanza)

    def send_message(self, to, type_, body, xhtml_body=None):
        msg = xmpp.Message(to=to, typ=type_, body=body)
        if xhtml_body:
            xhtml = xmpp.Node(xmpp.NS_XHTML_IM + " html")
            xbody = xmpp.Node("http://www.w3.org/1999/xhtml body")
            xbody.setPayload([xhtml_body])
            xhtml.setPayload([xbody])
            msg.addChild(node=xhtml)
        self.send(msg)

    def send_join(self, to, password=None):
        x = xmpp.Node(xmpp.NS_MUC+" x")
        if password:
            x.addChild("password", payload=password)
        x.addChild("history", attrs={"maxstanzas": "0"})
        room_jid = "%s/%s" % (to, self.res)
        self.send(xmpp.Presence(to=room_jid, payload=[x]))

    def join(self, room):
        if not room in self.rooms:
            self.send_join(*room)
            self.rooms.append(room)
            return True

    def leave(self, room):
        if room in self.rooms:
            room_jid = "%s/%s" % (room[0], self.res)
            prs = xmpp.Presence(
                to=room_jid, typ="unavailable", status="offline")
            self.send(prs)
            self.rooms.remove(room)
            return True

    def message_handler(self, cl, msg):
        # TODO: StopProcessing(Exception)
        for module in self.modules.values():
            if isinstance(module, modules.MessageModule):
                try:
                    module.handle(msg)
                except Exception:
                    traceback.print_exc()

    def presence_handler(self, cl, prs):
        # Allow owner's subscribe.
        if (prs.getType() == "subscribe" and
            prs.getFrom().getStripped() == self.owner):
                prs_to = xmpp.Presence(to=prs.getFrom(), typ="subscribed")
                self.send(prs_to)


# TODO: Refactor config.
if __name__ == "__main__":
    CC(config.user, config.rooms, config.owner).run()
