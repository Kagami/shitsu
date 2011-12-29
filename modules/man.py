import modules


class Module(modules.MessageModule):

    args = (0, 1)

    def run(self, module=None):
        """man [module]
        Show module's manual page.
        See also: help
        """
        if not module:
            return "What manual page do you want?"

        if module in self._bot.modules:
            man = self._bot.modules[module].run.__doc__
        else:
            man = None
        if man:
            return self.get_utils().trim(man)
        else:
            return "No manual entry for " + module
