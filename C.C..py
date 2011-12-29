#!/usr/bin/env python

##################################################
# C.C. - python xmpp bot
# Copyright (C) 2008-2012 Kagami <kagami@genshiken.org>
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

import os
import sys
os.chdir(sys.path[0])
import imp
import time
import signal
import logging
import traceback
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
try:
    import xmpp
except ImportError:
    path = os.path.join(os.path.dirname(__file__), 'lib')
    sys.path.insert(0, path)
    import xmpp
import utils
sys.path.insert(0, 'modules')
import config


class CC(object):

    RECONNECT_TIME = 30

    def __init__(self, user, rooms, owner):
        self._done = False
        self.cl = None
        self.jid = xmpp.JID(user[0])
        self.password = user[1]
        self.res = user[2]
        self.rooms = list(rooms)
        self.owner = owner

        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        signal.signal(signal.SIGTERM, sigterm_handler)

    def load(self, bot=None, args=None):
        """load
        Load all modules.
        See also: modprobe, rmmod, lsmod
        """
        if args: return
        self.userCommands  = {}
        self.ownerCommands = {
            'load': self.load,
            'modprobe': self.modprobe,
            'rmmod': self.rmmod,
        }
        for file in os.listdir('modules'):
            if (file.endswith('.py') and
                (file.startswith('user_') or file.startswith('owner_'))):
                    pos = file.index('_') + 1
                    self.modprobe(self, [file[pos:-3]])
        return 'done'

    def modprobe(self, bot, args):
        """modprobe <module>
        Load module.
        See also: load, rmmod, lsmod
        """
        if len(args) != 1: return

        name1 = 'user_%s' %args[0]
        name2 = 'owner_%s' %args[0]

        user = None
        try:
            file, pathname, description = imp.find_module(name1)
            user = True
            name = name1
        except:
            try:
                file, pathname, description = imp.find_module(name2)
                name = name2
            except:
                error = "MODULE: %s not found" % args[0]
                logging.error(error)
                return error

        try:
            method = imp.load_module(name, file, pathname, description).main
        except:
            error = "MODULE: can't load %s" % args[0]
            logging.error(error)
            return error
        else:
            if user:
                self.userCommands[args[0]] = method
            else:
                self.ownerCommands[args[0]] = method

        info = "MODULE: %s loaded" % args[0]
        logging.info(info)
        return info

    def rmmod(self, bot, args):
        """rmmod <module>
        Remove module.
        See also: load, modprobe, lsmod
        """
        if len(args) != 1: return

        if args[0] == 'load' or args[0] == 'modprobe' or args[0] == 'rmmod':
            return "MODULE: can't remove %s" % args[0]

        if self.userCommands.has_key(args[0]):
            del self.userCommands[args[0]]
        elif self.ownerCommands.has_key(args[0]):
            del self.ownerCommands[args[0]]
        else:
            return "MODULE: %s not loaded" % args[0]

        info = "MODULE: %s removed" % args[0]
        logging.info(info)
        return info

    def run(self):
        self.load()
        while not self._done:
            try:
                if self.cl is None:
                    if self.connect():
                        logging.info('CONNECTION: bot connected')
                    else:
                        time.sleep(self.RECONNECT_TIME)
                else:
                    self.cl.Process(1)
            except xmpp.protocol.XMLNotWellFormed:
                logging.error('CONNECTION: reconnect (detected not valid XML)')
                self.cl = None
            except (KeyboardInterrupt, SystemExit):
                self.exit('EXIT: interrupted by SIGTERM')

    def connect(self):
        self.cl = xmpp.Client(self.jid.getDomain(), debug = [])
        if not self.cl.connect():
            logging.error('CONNECTION: unable to connect to server')
            return
        if not self.cl.auth(self.jid.getNode(), self.password, self.res):
            logging.error('CONNECTION: unable to authorize with server')
            return
        for room in self.rooms:
            self.send_join(*room)
        self.cl.RegisterHandler('message', self.message_handler)
        self.cl.RegisterHandler('presence', self.presence_handler)
        self.cl.sendPresence()
        return True

    def exit(self, msg='exit'):
        if self.cl is None:
            return
        for room in self.rooms:
            self.leave(room)
        try:
            self.cl.disconnect()
        except AttributeError:
            # TODO: Why does this happen on disconnect?
            # %%C.O.: xmpppy is crap%%
            pass
        logging.info(msg)
        self._done = True

    def send(self, stanza):
        if not self._done:
            self.cl.send(stanza)

    def send_message(self, to, type_, text, extra=None):
        msg = xmpp.Message(to=to, typ=type_, body=text)
        if extra:
            xhtml = xmpp.Node(xmpp.NS_XHTML_IM + ' html')
            body = xmpp.Node('http://www.w3.org/1999/xhtml body')
            body.setPayload([extra])
            xhtml.setPayload([body])
            msg.addChild(node=xhtml)
        self.send(msg)

    def send_join(self, to, password=None):
        x = xmpp.Node(xmpp.NS_MUC+' x')
        if password:
            x.addChild('password', payload=password)
        x.addChild('history', attrs={'maxstanzas': '0'})
        room_jid = '%s/%s' % (to, self.res)
        self.send(xmpp.Presence(to=room_jid, payload=[x]))

    def join(self, room):
        if not room in self.rooms:
            self.send_join(*room)
            self.rooms.append(room)
            return True

    def leave(self, room):
        if room in self.rooms:
            room_jid = '%s/%s' % (room[0], self.res)
            prs = xmpp.Presence(
                to=room_jid, typ='unavailable', status='offline')
            self.send(prs)
            self.rooms.remove(room)
            return True

    def is_from_room(self, jid):
        for room in self.rooms:
            if room[0] == jid:
                return True

    def message_handler(self, cl, msg):
        type_ = msg.getType()
        from_ = msg.getFrom()
        user = from_.getStripped()
        prefix = from_.getResource()
        text = utils.force_unicode(msg.getBody())
        if ((not prefix) or (type_ == 'groupchat' and prefix == self.res) or
            (not text)):
            return

        # Check command.
        if text[0] == '%':
            text = text[1:]
        else:
            if type_ == 'groupchat':
                url_match = utils.url_re.search(text)
                if url_match is not None:
                    url = url_match.group()
                    title = utils.getTitle(url)
                    if title:
                        self.send_message(user, type_, 'Title: ' + title)
            return

        # Parse command.
        spl = text.split()
        if spl:
            cmd, args = spl[0], spl[1:]
        else:
            return

        if self.is_from_room(user):
            # Message from room.
            if self.owner[1]:
                owner = prefix == self.owner[1]
            else:
                owner = False
        else:
            # Message to bot's jid.
            owner = user == self.owner[0]

        if type_ == 'groupchat':
            if '>' in args:
                # Redirect output.
                index  = args.index('>')
                prefix = ''
                redir  = ' '.join(args[index+1:])
                if redir:
                    prefix = redir + ', '
                args   = args[:index]
            else:
                # Groupchat => prefix
                prefix += ', '
        else:
            # Chat => no prefix
            user, prefix = from_, ''

        # Execute command.
        error = None
        if self.userCommands.has_key(cmd):
            try:
                result = self.userCommands[cmd](self, args)
            except:
                error = True
        elif self.ownerCommands.has_key(cmd):
            if owner:
                try:
                    result = self.ownerCommands[cmd](self, args)
                except:
                    error = True
            else:
                result = 'access denied'
        else:
            return

        if error:
            error = 'MODULE: exception in %s' %(cmd)
            logging.error(error + '\n' + traceback.format_exc()[:-1])
            msg, extra = error, ''
        else:
            if result:
                if isinstance(result, tuple):
                    msg, extra = result
                else:
                    msg, extra = result, ''
            else:
                msg, extra = 'invalid syntax', ''

        if msg:
            self.send_message(
                user, type_,
                prefix + utils.force_unicode(msg), extra)

    def presence_handler(self, cl, prs):
        # Allow owner's subscribe.
        if (prs.getType() == 'subscribe' and
            prs.getFrom().getStripped() == self.owner[0]):
                prs_to = xmpp.Presence(to=prs.getFrom(), typ='subscribed')
                self.send(prs_to)


def sigterm_handler(signum, frame):
    raise SystemExit


if __name__ == '__main__':
    CC(config.user, config.rooms, config.owner).run()
