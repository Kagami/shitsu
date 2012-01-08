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

from shitsu import modules
from shitsu import utils
reload(utils)


class Help(modules.MessageModule):

    args = (0,)

    def run(self):
        commands = []
        for module in self._bot.modules.values():
            if (isinstance(module, modules.MessageModule) and
                module.regexp is None):
                    commands.append(module.name)
        commands.sort()
        commands = ", ".join(commands)
        return utils.trim("""
            Basic bot usage: %%<command> <args>
            Available commands: %s
            Type %%man -v <command> to show command's manual page.
            Sources and bug tracker: https://github.com/Kagami/shitsu
            """ % commands)


class Man(modules.MessageModule):

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
                if (isinstance(module, modules.MessageModule) and man and
                    module.regexp is None):
                        man = utils.trim(command + " " + man)
                        if verbose:
                            user_acl = kwargs["add"]["user_acl"]
                            man = ("%s\n\nMinimum access level required: %s\n"
                                   "Your access level: %s" % (
                                        man, module.acl, user_acl))
                        return man
                else:
                        return not_found
        return not_found
