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

import os
import imp
import logging
from shitsu import modules
from shitsu.utils import config
reload(config)


class Load(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0,)

    def run(self):
        """
        (Re)load config and modules.
        See also: modprobe, rmmod, lsmod
        """
        path = self._bot.options.config_path
        self._bot.cfg = config.Config(path).get_sect("main")
        self._bot.modules = {}
        modprobe = Modprobe(self._bot)
        modules = []
        for d in self._bot.options.modules_dirs:
            modules.extend(os.listdir(d))
        for module_name in modules:
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
            info = imp.find_module(module_file, self._bot.options.modules_dirs)
            mod = imp.load_module(module_file, *info)
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (type(attr) is type and
                    issubclass(attr, modules.BaseModule)):
                        module = attr(self._bot, module_file)
                        self._bot.modules[module.name] = module
        except Exception:
            error = "FILE: can't load %s" % module_file
            logging.exception(error)
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
