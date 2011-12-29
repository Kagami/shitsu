import re
import logging
import traceback


class ACL(object):
    """Access level class."""

    def __init__(self, value, desc):
        self._value = value
        self._desc = desc

    def __cmp__(self, other):
        if not isinstance(other, ACL):
            raise NotImplemented
        if self._value < other._value:
            return -1
        elif self._value == other._value:
            return 0
        else:
            return 1

    def __str__(self):
        return self._desc


# Access level constants.
ACL_ANY = ACL(0, "any")
ACL_OWNER = ACL(7, "owner")


class MessageModule(object):
    """Base class for message modules."""

    prefix = "%"  # TODO: Set it via config.
    use_prefix = True  # Should command be prefixed.
    name = None  # Module name (if not specified get it from file name).
    acl = ACL_ANY  # Minimum access level required to use command.
    re = None  # Command regexp (if not specified match by name).
    raw_query = False  # If true module will get raw query string.
    args = ()  # List of correct arguments number. (1, 3) means 1 or 3.
               # Empty list means any number.

    def __init__(self, module_name, bot):
        self._bot = bot
        self.name = self.name if self.name else module_name
        if self.re is not None:
            self.rec = re.compile(self.re)
        else:
            self.rec = None

    def get_user_acl(self, msg):
        if msg.getFrom().getStripped() == self._bot.owner:
            return ACL_OWNER
        else:
            return ACL_ANY

    def is_allowed(self, msg):
        if self.get_user_acl(msg) < self.acl:
            return False
        else:
            return True

    def handle(self, msg):
        type_ = msg.getType()
        from_ = msg.getFrom()
        resource = from_.getResource()
        body = msg.getBody()
        if type_ not in ("chat", "groupchat"):
            return
        # TODO: Subject catch (empty resource).
        if ((not resource) or
            (type_ == "groupchat" and resource == self._bot.res)):
                return
        if body is None:
            body = ""
        args = None
        if self.rec is not None:
            match = self.rec.search(body)
            if match is not None:
                args = match.groups()
        else:
            if self.use_prefix:
                if not body.startswith(self.prefix):
                    return
                body = body[len(self.prefix):]
            if not body.startswith(self.name):
                return
            query = body[len(self.name):]
            if query and query[0] != " ":
                return
            query = query[1:]
            if self.raw_query:
                args = [query]
            else:
                args = query.split()
                if self.args and len(args) not in self.args:
                    self.send_message(msg, "invalid syntax")
                    return
        if args is None:
            return
        if self.is_allowed(msg):
            self.run_and_send_result(msg, *args)
        else:
            self.send_message(msg, "access denied")

    def run_and_send_result(self, msg, *args):
        body = None
        xhtml_body = None
        try:
            # TODO: Threading.
            result = self.run(*args)
        except Exception:
            error = "MODULE: exception in " + self.name
            logging.error("%s\n%s" % (
                error, traceback.format_exc()[:-1]))
            body = error
        else:
            if result is None:
                body = "invalid syntax"
            elif type(result) is tuple:
                body, xhtml_body = result
            else:
                body = result
        if body:
            self.send_message(msg, body, xhtml_body)

    def send_message(self, msg, body, xhtml_body=None):
        type_ = msg.getType()
        from_ = msg.getFrom()
        from_jid = from_.getStripped()
        resource = from_.getResource()
        if type_ == "chat":
            to = from_
            prefix = ""
        else:
            to = from_jid
            prefix = resource + ", "
        body = prefix + body
        self._bot.send_message(to, type_, body, xhtml_body)

    def run(self, *args):
        """Main module's function.
        Get:
        match.groups() if self.re is not None
        splitted list of arguments otherwise
        Return:
        string (str on unicode) on simple result
        tuple of 2 strings as result body and xhtml body
        empty string if nothing should be sended back to user
        None on invalid syntax
        """
