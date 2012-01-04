import re
import modules


class Alias(modules.MessageModule):

    acl = modules.ACL_OWNER
    raw_query = True

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
        Set/del/show aliases.
        Usage:
        %alias           # show all available aliases
        %alias %c        # show alias for %c
        %alias %c=%cmd   # set alias %c = %cmd
        (%c will be expanded as %cmd; all args preserved)
        %alias %c=       # delete alias %c
        You could also omit prefix if you wish:
        %alias man=%man  # man will be expanded as %man
        You could use $1-$9 magic varaiables to expand command arguments:
        %alias %cjo=%disco $1@conference.jabber.org
        (%cjo room will be expanded as %disco test@conference.jabber.org)
        """
        # Show all.
        if not query:
            aliases = []
            for alias, (value, _, _) in self._bot.aliases.items():
                aliases.append("%s = %s" % (alias, value))
            if not aliases:
                return "no aliases defined"
            else:
                return "Aliases:\n" + "\n".join(aliases)
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
                        query = " " + " ".join(dargs.values())
                body = value + query
                msg = add["msg"]
                msg.setBody(body)
                module.handle(msg)
                return ""
        return ""
