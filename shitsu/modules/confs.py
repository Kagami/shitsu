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


class Join(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0, 1)
    thread_safe = False

    def run(self, conf=None, permanent=True):
        """[conf]
        Join the conference and add it to the startup
        conference list.
        Format: conf@conference.jabber.org[/nickname][:password]
        Without arguments show the list of conferences
        where the bot is resident.
        """
        if conf:
            if ":" in conf:
                conf, password = conf.split(":", 1)
            else:
                password = None
            conf_jid = xmpp.JID(conf)
            bare = conf_jid.getStripped()
            if bare in self._bot.confs:
                return "I'm already in this conference"
            if not conf_jid.getResource():
                conf_jid.setResource(
                    self.cfg.get("default_nickname", "shitsu"))
            self._bot.send_join(conf_jid, password)
            self._bot.confs[bare] = {
                "nickname": conf_jid.getResource()
            }
            if permanent:
                confs = "\n" + "\n".join(self.cfg.conferences.split() + [conf])
                self.cfg.set("conferences", confs)
            return "joined"
        else:
            confs = []
            for jid, v in self._bot.confs.items():
                confs.append("%s/%s" % (jid, v["nickname"]))
            if confs:
                return "I'm currently in:\n" + "\n".join(confs)
            else:
                return "I'm not in any conference."


class Leave(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (1,)
    thread_safe = False

    def run(self, jid, permanent=True):
        """<jid>
        Leave conference and remove it from the startup
        conference list.
        """
        conf_jid = xmpp.JID(jid)
        bare = conf_jid.getStripped()
        if bare in self._bot.confs:
            conf_jid.setResource(self._bot.confs[bare]["nickname"])
            self._bot.send_leave(conf_jid)
            del self._bot.confs[bare]
            if permanent:
                confs = "\n" + "\n".join(filter(
                    lambda c: not c.startswith(bare),
                    self.cfg.conferences.split()))
                self.cfg.set("conferences", confs)
            return "left"
        else:
            return "I'm not in " + jid


class JoinConfs(modules.ConnectModule):

    def run(self):
        join = self._bot.modules["join"]
        confs = self.cfg.conferences.split()
        for conf in confs:
            join.run(conf, False)


class LeaveConfs(modules.DisconnectModule):

    def run(self):
        leave = self._bot.modules["leave"]
        jids = self._bot.confs.keys()
        for jid in jids:
            leave.run(jid, False)
