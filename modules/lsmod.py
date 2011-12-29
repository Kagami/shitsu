import modules


class Module(modules.MessageModule):

    args = (0,)

    def run(self):
        """lsmod
        Show list of loaded modules.
        See also: load, modprobe, rmmod
        """
        result = []
        return "Loaded modules: " + ", ".join(self._bot.modules)
