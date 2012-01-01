import modules


class Module(modules.MessageModule):

    args = (0, 1, 2)
    additional_args = True

    def run(self, *args, **kwargs):
        """[[-v] command]
        Show command's manual page.
        If verbose flag specified show acl info.
        See also: help
        """
        if not args:
            return "What manual page do you want?"
        elif len(args) == 1:
            command = args[0]
            verbose = False
        elif args[0] == "-v":
            command = args[1]
            verbose = True
        else:
            return

        not_found = "No manual entry for " + command
        for module in self._bot.modules.values():
            if module.name == command:
                man = module.run.__doc__
                if isinstance(module, modules.MessageModule) and man:
                    man = self.get_utils().trim(command + " " + man)
                    if verbose:
                        user_acl = kwargs["add"]["user_acl"]
                        man = ("%s\n\nMinimum access level required: %s\n"
                               "Your access level: %s" % (
                                    man, module.acl, user_acl))
                    return man
                else:
                    return not_found
        return not_found
