import re
import logging
import traceback
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import xmpp
import utils


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
ACL_NONE = ACL(0, "none")
ACL_OWNER = ACL(7, "owner")


class BaseModule(object):

    def __init__(self, bot, config_section=None):
        self.name = self.__class__.__name__.lower()
        self._bot = bot
        if bot and bot.cfg:
            if not config_section: config_section = self.name
            self.cfg = bot.cfg._config.get_sect(config_section)

    def load(self):
        """Called on config update."""

    def run(self):
        """Main module function. All hard work goes here."""


class MessageModule(BaseModule):
    """Base class for message modules."""

    use_prefix = True  # Is command should be prefixed.
    acl = ACL_NONE  # Minimum access level required to use command.
    regexp = None  # Command regexp (if not specified match by name).
    types = ("chat", "groupchat")  # Process messages only with
                                   # specified types.
    _all_types = ("chat", "groupchat")  # Don't touch this.
    raw_query = False  # If true module will get raw query string.
    args = ()  # List of correct arguments number. (1, 3) means 1 or 3.
               # Empty list means any number.
    highlight = True  # Highlight users in groupchats with command's result.
    additional_args = False  # Send to module some additional args such as
                             # original stanza and user acl.

    def __init__(self, bot, config_section=None):
        super(MessageModule, self).__init__(bot, config_section)
        if self.regexp is not None:
            self.rec = re.compile(self.regexp)
        else:
            self.rec = None

    def get_user_acl(self, msg):
        if msg.getFrom().getStripped() == self._bot.cfg.owner_jid:
            return ACL_OWNER
        else:
            return ACL_NONE

    def is_allowed(self, user_acl):
        if user_acl < self.acl:
            return False
        else:
            return True

    def copy_msg(self, msg):
        copy = xmpp.simplexml.XML2Node(unicode(msg).encode("utf-8"))
        return xmpp.Message(node=copy)

    def handle(self, msg):
        type_ = msg.getType()
        from_ = msg.getFrom()
        from_jid = from_.getStripped()
        resource = from_.getResource()
        body = msg.getBody()
        if type_ not in self._all_types or type_ not in self.types:
            return
        if type_ == "chat" and (from_jid not in self._bot.confs and
                                from_jid != self._bot.cfg.owner_jid):
            return
        # TODO: Subject catch (empty resource).
        if ((not resource) or
            (type_ == "groupchat" and
             resource == self._bot.confs[from_jid]["nickname"])):
                return
        if body is None:
            body = ""
        if self.rec is not None:
            match = self.rec.search(body)
            if match:
                args = match.groups()
            else:
                return
        else:
            if self.use_prefix:
                if not body.startswith(self._bot.cfg.prefix):
                    return
                body = body[len(self._bot.cfg.prefix):]
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
        user_acl = self.get_user_acl(msg)
        if self.is_allowed(user_acl):
            if self.additional_args:
                msg_copy = self.copy_msg(msg)
                kwargs = {"add": {
                    "msg": msg_copy, "user_acl": user_acl},
                }
            else:
                kwargs = {}
            self.run_and_send_result(msg, *args, **kwargs)
        else:
            self.send_message(msg, "access denied")

    def run_and_send_result(self, msg, *args, **kwargs):
        body = None
        xhtml_body = None
        try:
            # TODO: Threading.
            result = self.run(*args, **kwargs)
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
        elif type_ == "groupchat":
            to = from_jid
            if self.highlight:
                prefix = resource + ", "
                body = prefix + body
                if xhtml_body:
                    xhtml_body = prefix + xhtml_body
        else:
            raise NotImplemented
        limit = self._bot.cfg.max_message_length
        if len(body) > limit:
            body = body[:limit] + u"\u2026"
        if xhtml_body and len(xhtml_body) > limit:
            # We can't just cut xml.
            xhtml_body = None
        self._bot.send_message(to, type_, body, xhtml_body)

    def run(self, *args):
        """Main module function.
        Get:
        - match.groups() if module's regexp specified
        - splitted list of arguments otherwise
        See also module's additional options.
        Return:
        - string on simple result
        - tuple of 2 strings as result body and xhtml body
        - empty string if nothing should be sended back to user
        - None on invalid syntax
        Note that if result string has non-ascii symbols it MUST
        be unicode string. Input args conform the same rule.
        """


class ConnectModule(BaseModule):
    """Module which will be started just after
    connecting bot to server.
    """


class DisconnectModule(BaseModule):
    """Module which will be started just before
    bot's disconnect.
    """
