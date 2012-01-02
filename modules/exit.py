import modules


class Exit(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0,)

    def run(self):
        """
        Leave all conferences, disconnect and exit.
        """
        self._bot.exit()
        return ""
