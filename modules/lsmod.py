import modules


class Lsmod(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0,)

    def run(self):
        """
        Show list of loaded modules.
        See also: load, modprobe, rmmod
        """
        result = []
        return "Loaded modules: " + ", ".join(self._bot.modules)
