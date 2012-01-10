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
import logging
import threading
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from shitsu import xmpp
from shitsu import utils


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
    allow_conf_private = True  # Allow or not module use in private
                               # conference chats.
    raw_query = False  # If true module will get raw query string.
    args = ()  # List of correct arguments number. (1, 3) means 1 or 3.
               # Empty list means any number.
    highlight = True  # Highlight users in groupchats with command's result.
    additional_args = False  # Send to module some additional args such as
                             # original stanza and user acl.
    thread_safe = True  # Is module thread-safe and can be run multiple
                        # times in parallel or not.

    def __init__(self, bot, config_section=None):
        super(MessageModule, self).__init__(bot, config_section)
        # Have actual value only if module is not thread-safe.
        # Please do not rely up to this otherwise.
        self._running = False
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
        if self._bot.threads_num >= int(self._bot.cfg.max_threads_num):
            return
        type_ = msg.getType()
        from_ = msg.getFrom()
        from_jid = from_.getStripped()
        resource = from_.getResource()
        body = msg.getBody()
        if body is None:
            body = ""
        if type_ not in self.types:
            return
        if type_ == "chat":
            if from_jid in self._bot.confs:
                if not self.allow_conf_private:
                    return
            elif from_jid != self._bot.cfg.owner_jid:
                return
        # TODO: Subject catch (empty resource).
        if ((not resource) or
            (type_ == "groupchat" and
             resource == self._bot.confs[from_jid]["nickname"])):
                return
        if self.rec is not None:
            match = self.rec.search(body)
            if match:
                args = match.groups()
            else:
                return
        else:
            if self.use_prefix:
                prefix = self._bot.cfg.get("prefix", "%")
                if not body.startswith(prefix):
                    return
                body = body[len(prefix):]
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
        if not self.is_allowed(user_acl):
            self.send_message(msg, "access denied")
            return
        if not self.thread_safe and self._running:
            self.send_message(msg, "already running")
            return
        # Run module in thread.
        args = [msg] + list(args)
        if self.additional_args:
            msg_copy = self.copy_msg(msg)
            kwargs = {"add": {"msg": msg_copy, "user_acl": user_acl}}
        else:
            kwargs = {}
        self._running = True
        self._bot.threads_num += 1
        threading.Thread(
            target=self.run_and_send_result,
            args=args, kwargs=kwargs).start()

    def run_and_send_result(self, msg, *args, **kwargs):
        body = None
        xhtml_body = None
        try:
            result = self.run(*args, **kwargs)
        except Exception:
            error = "MODULE: exception in " + self.name
            logging.exception(error)
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
        self._bot.threads_num -= 1
        self._running = False

    def send_message(self, msg, body, xhtml_body=None, type_=None):
        if not type_: type_ = msg.getType()
        from_ = msg.getFrom()
        from_jid = from_.getStripped()
        resource = from_.getResource()
        if type_ == "chat":
            # TODO: Several splitted messages.
            to = from_
            limit = int(self._bot.cfg.get("max_chat_length", 5000))
            if len(body) > limit:
                body = body[:limit] + u"\u2026"
            if xhtml_body and len(xhtml_body) > limit * 2:
                # We can't just cut xml so throw it.
                xhtml_body = None
        elif type_ == "groupchat":
            to = from_jid
            old_body = body
            old_xhtml = xhtml_body
            if self.highlight:
                prefix = resource + ", "
                body = prefix + body
                if xhtml_body:
                    xhtml_body = prefix + xhtml_body
            limit = int(self._bot.cfg.get("max_groupchat_length", 1000))
            too_big = False
            if len(body) > limit:
                body = body[:limit] + u"\u2026"
                too_big = True
            if xhtml_body and len(xhtml_body) > limit * 2:
                # We can't just cut xml so throw it.
                xhtml_body = None
                too_big = True
            if too_big:
                # Send remaining text to private.
                self.send_message(msg, old_body, old_xhtml, "chat")
        else:
            raise NotImplemented
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
    connecting to the server.
    """


class DisconnectModule(BaseModule):
    """Module which will be started just before
    disconnect.
    """
