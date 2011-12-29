import modules


class Module(modules.MessageModule):

    args = (0,)

    def run(self):
        """lsmod
        Show list of loaded modules.
        See also: load, modprobe, rmmod
        """
        result = ["Avialable modules:"]
        for module_name, module in self._bot.modules.items():
            result.append("%s; acl: %s" % (module_name, module.acl))
        return "\n".join(result)
