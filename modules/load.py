import os
import modules
import modules.modprobe


class Module(modules.MessageModule):

    acl = modules.ACL_OWNER
    args = (0,)

    def run(self):
        """load
        Load all modules.
        See also: modprobe, rmmod, lsmod
        """
        self._bot.modules = {}
        modprobe = modules.modprobe.Module("modprobe", self._bot)
        for module_name in os.listdir("modules"):
            if (module_name.startswith("_") or
                module_name.startswith(".") or
                not module_name.endswith(".py")):
                    continue
            module_name = module_name[:-3]
            modprobe.run(module_name)
        return "done"
