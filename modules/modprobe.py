import imp
import logging
import traceback
import modules


class Module(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (1,)

    def run(self, module_name):
        """<module>
        Load module.
        See also: load, rmmod, lsmod
        """
        try:
            (file_, path, desc) = imp.find_module(module_name, ["modules"])
            mod = imp.load_module(module_name, file_, path, desc).Module
            self._bot.modules[module_name] = mod(module_name, self._bot)
        except Exception:
            error = "MODULE: can't load %s" % module_name
            logging.error("%s\n%s" % (error, traceback.format_exc()[:-1]))
            return error
        else:
            info = "MODULE: %s loaded" % module_name
            logging.info(info)
            return info
