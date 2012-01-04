import os
import imp
import logging
import traceback
from utils import config
reload(config)
import modules


class Load(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0,)

    def run(self):
        """
        (Re)load config and modules.
        See also: modprobe, rmmod, lsmod
        """
        self._bot.cfg = config.Config().get_sect("main")
        self._bot.modules = {}
        modprobe = Modprobe(self._bot)
        for module_name in os.listdir("modules"):
            if (module_name.startswith("_") or
                module_name.startswith(".") or
                not module_name.endswith(".py")):
                    continue
            module_name = module_name[:-3]
            modprobe.run(module_name)
        for module in self._bot.modules.values():
            module.load()
        return "done"


class Modprobe(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (1,)

    def run(self, module_file):
        """<module_file>
        Load all modules from module's file.
        For `modules/animecal.py' command
        will looks like `%modprobe animecal'.
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


class Rmmod(modules.MessageModule):

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


class Exit(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0,)

    def run(self):
        """
        Leave all conferences, disconnect and exit.
        """
        self._bot.exit()
        return ""
