import imp
import logging
import traceback
import modules


class Modprobe(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (1,)

    def run(self, module_file):
        """<module_file>
        Load all modules from module's file.
        For `modules/anime_cal.py' command
        will looks like `%modprobe anime_cal'.
        See also: load, rmmod, lsmod
        """
        try:
            (file_, path, desc) = imp.find_module(module_file, ["modules"])
            mod = imp.load_module(module_file, file_, path, desc)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (type(attr) is type and
                    issubclass(attr, modules.BaseModule)):
                        module = attr(self._bot, module_file)
                        self._bot.modules[module.name] = module
        except Exception:
            error = "FILE: can't load %s" % module_file
            logging.error("%s\n%s" % (error, traceback.format_exc()[:-1]))
            return error
        else:
            info = "FILE: %s loaded" % module_file
            logging.info(info)
            return info
