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

import re
from shitsu import modules


class Aliases(modules.MessageModule):

    args = (0,)

    def run(self):
        """
        Show all available aliases.
        """
        aliases = []
        for alias, (value, _, _) in self._bot.aliases.items():
            aliases.append("%s = %s" % (alias, value))
        if not aliases:
            return "no aliases defined"
        else:
            return "Aliases:\n" + "\n".join(aliases)


class Alias(modules.MessageModule):

    acl = modules.ACL_OWNER
    raw_query = True
    thread_safe = False

    def load(self):
        self._bot.aliases = {}
        for alias, value in self.cfg.items():
            self.add_alias(alias, value)

    def add_alias(self, alias, value):
        # Search module which should be run on alias.
        for module in self._bot.modules.values():
            if (isinstance(module, modules.MessageModule) and
                module.rec is None):
                    name = module.name
                    if module.use_prefix:
                        name = self._bot.cfg.prefix + name
                    r = r"^%s(?: |$)" % re.escape(name)
                    if re.match(r, value):
                        # Module name matched. Create alias.
                        regexp = "^%s(?: |$)" % re.escape(alias)
                        self._bot.aliases[alias] = (
                            value, re.compile(regexp), module)
                        return True

    def run(self, query):
        """[cmd[=[command]]]
        Set/del/show alias.

        Show alias for %c:
        %alias %c

        Set alias %c = %cmd:
        (%c will be expanded as %cmd; all args preserved)
        %alias %c=%cmd

        Delete alias %c:
        %alias %c=

        You could also omit prefix if you wish:
        (man will be expanded as %man)
        %alias man=%man

        You could use $1-$9 magic varaiables to expand command arguments:
        %alias %cjo=%disco $1@conference.jabber.org
        (`%cjo room' will be expanded as `%disco room@conference.jabber.org')
        """
        if not query:
            return
        # Show.
        if "=" not in query:
            if query in self._bot.aliases:
                return "%s = %s" % (query, self._bot.aliases[query][0])
            else:
                return "no such alias"
        alias, value = query.split("=", 1)
        # Set.
        if value:
            if self.add_alias(alias, value):
                self.cfg.set(alias, value)
                return "defined"
            else:
                return "bad alias"
        # Del.
        if alias in self._bot.aliases:
            del self._bot.aliases[alias]
            self.cfg.remove(alias)
            return "deleted"
        else:
            return "no such alias"


class ProcessAliases(modules.MessageModule):

    regexp = "(.*)"
    additional_args = True

    def run(self, query, add):
        for alias, (value, rec, module) in self._bot.aliases.items():
            if rec.match(query):
                query = query[len(alias):]
                # Do interpolation.
                interpolated = False
                # Split only 9 first args.
                dargs = dict(zip(xrange(1, 11), query.split(None, 9)))
                # Interpolate $1-$9.
                for i in xrange(1, 10):
                    if re.search(r"\$%d" % i, value):
                        interpolated = True
                        if i in dargs:
                            arg = dargs[i]
                            del dargs[i]
                        else:
                            arg = ""
                        value = re.sub(r"\$%d" % i, arg, value)
                # Join remaining args.
                if interpolated:
                    if not dargs:
                        query = ""
                    else:
                        # Dict is orderless, so we should sort it by ourself.
                        dargs = sorted(dargs.items())
                        query = " " + " ".join(map(lambda i: i[1], dargs))
                body = value + query
                msg = add["msg"]
                msg.setBody(body)
                module.handle(msg)
                return ""
        return ""
