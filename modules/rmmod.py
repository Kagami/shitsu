import logging
import modules


class Module(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (1,)

    def run(self, module_name):
        """rmmod <module>
        Remove module.
        See also: load, modprobe, lsmod
        """
        if module_name in self._bot.modules:
            del self._bot.modules[module_name]
            info = "MODULE: %s removed" % module_name
            logging.info(info)
            return info
        else:
            return "MODULE: %s not loaded" % module_name
