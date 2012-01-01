import modules
import utils
reload(utils)


class Module(modules.MessageModule):

    args = (0,)

    def run(self):
        commands = []
        for module in self._bot.modules.values():
            if isinstance(module, modules.MessageModule):
                commands.append(module.name)
        commands.sort()
        commands = ", ".join(commands)
        return utils.trim("""
            Basic bot usage: %%<command> <args>
            Available commands: %s
            Type %%man -v <command> to show command's manual page.
            Sources and bug tracker: https://github.com/Kagami/C.C.
            """ % commands)
