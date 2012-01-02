import xmpp
import modules


class Join(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0, 1)

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
                conf_jid.setResource(self.cfg.default_nickname)
            self._bot.send_join(conf_jid, password)
            self._bot.confs[bare] = {
                "nickname": conf_jid.getResource()
            }
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
            return "left"
        else:
            return "I'm not in " + jid


class JoinConfs(modules.ConnectModule):

    def run(self):
        join = self._bot.modules["join"]
        self._bot.confs = {}
        confs = self.cfg.conferences.split()
        for conf in confs:
            join.run(conf, False)


class LeaveConfs(modules.DisconnectModule):

    def run(self):
        leave = self._bot.modules["leave"]
        jids = self._bot.confs.keys()
        for jid in jids:
            leave.run(jid, False)
