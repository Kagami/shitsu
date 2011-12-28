import os
import sys
import imp
import time
import signal
import random
import logging
import datetime
from xml.sax.saxutils import escape, unescape
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
try:
    import xmpp
except ImportError:
    path = os.path.join(os.path.dirname(__file__), 'lib')
    sys.path.insert(0, path)
    import xmpp
import misc
sys.path.insert(0, 'modules')


class JabberBot(object):

    reconnectTime = 30

    def __init__(self, user, rooms, owner):
        signal.signal(signal.SIGTERM, sigTermCB)
        try:
            signal.signal(signal.SIGHUP,  sigHupCB)
        except AttributeError:
            # Don't work on Windows and maybe on some other OSes.
            # TODO: More graceful check?
            pass

        self.jid = xmpp.JID(user[0])
        self.password = user[1]
        self.res = user[2]
        self.rooms = list(rooms)
        self.owner = owner
        self.conn = None
        self.__finished = False
        self.iq = True
        self.last = datetime.datetime(1, 1, 1)

        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

    def load(self, bot=None, args=None):
        '''load\nLoad all modules.\nSee also: modprobe, rmmod, lsmod'''

        if args: return

        self.userCommands  = {}
        self.ownerCommands = {'load': self.load, 'modprobe': self.modprobe, 'rmmod': self.rmmod}

        for file in os.listdir('modules'):
            if file.endswith('.py') and (file.startswith('user_') or file.startswith('owner_')):
                pos = file.index('_') + 1
                self.modprobe(self, [file[pos:-3]])

        return 'done'

    def modprobe(self, bot, args):
        '''modprobe <module>\nLoads module.\nSee also: load, rmmod, lsmod'''

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
                error = 'MODULE: %s not found' %args[0]
                logging.error(error)
                return error

        try:
            method = imp.load_module(name, file, pathname, description).main
        except:
            error = 'MODULE: can\'t load %s' %args[0]
            logging.error(error)
            return error
        else:
            if user:
                self.userCommands[args[0]] = method
            else:
                self.ownerCommands[args[0]] = method

        info = 'MODULE: %s loaded' %args[0]
        logging.info(info)
        return info

    def rmmod(self, bot, args):
        '''rmmod <module>\nRemove module.\nSee also: load, modprobe, lsmod'''

        if len(args) != 1: return

        if args[0] == 'load' or args[0] == 'modprobe' or args[0] == 'rmmod':
            return 'MODULE: can\'t remove %s' %args[0]

        if self.userCommands.has_key(args[0]):
            del self.userCommands[args[0]]
        elif self.ownerCommands.has_key(args[0]):
            del self.ownerCommands[args[0]]
        else:
            return 'MODULE: %s not loaded' %args[0]

        info = 'MODULE: %s removed' %args[0]
        logging.info(info)
        return info

    def connect(self):
        if not self.conn:
            conn = xmpp.Client(self.jid.getDomain(), debug = [])

            if not conn.connect():
                logging.error('CONNECTION: unable to connect to server')
                return

            if not conn.auth(self.jid.getNode(), self.password, self.res):
                logging.error('CONNECTION: unable to authorize with server')
                return

            for room in self.rooms:
                self._join_presence(conn, room[0], room[1])

            conn.RegisterHandler('message', self.messageCB)
            conn.RegisterHandler('presence', self.presenceCB)
            conn.RegisterHandler('iq', self.iqCB, typ='result', ns=xmpp.NS_TIME)
            conn.sendInitPresence()

            self.conn = conn
            return True

    def exit(self, msg = 'exit'):
        if self.conn:
            for room in self.rooms:
                self.leave(room)
            self.conn = None

        self.__finished = True
        logging.info(msg)

    def _validate(self, text):
        return escape(unescape(text, {
            '&quot;': '\'',
            '&#39;': '\'',
            '&#44;': ',',
            '&middot;': u'\xb7'}))

    def send(self, user, type, text, extra = ''):
        self.conn.send(u'<message to="%s" type="%s"><body>%s</body>%s</message>' %(user, type, self._validate(text), extra))

    def _join_presence(self, conn, room, password=None):
        if password:
            conn.send('<presence to=\'%s/%s\'><x xmlns=\'http://jabber.org/protocol/muc\'><password>%s</password></x></presence>'
                      %(room, self.res, password))
        else:
            conn.send(xmpp.Presence(to='%s/%s' %(room, self.res)))

    def join(self, room):
        if not room in self.rooms:
            self._join_presence(self.conn, room[0], room[1])
            self.rooms.append(room)
            return True

    def leave(self, room):
        if room in self.rooms:
            self.conn.send(xmpp.Presence(to='%s/%s' %(room[0], self.res), typ='unavailable', status='offline'))
            self.rooms.remove(room)
            return True

    def _inRoom(self, user):
        for room in self.rooms:
            if room[0] == user:
                return True

    def messageCB(self, conn, mess):
        # Just a history
        if mess.getTimestamp():
            return

        type = mess.getType()
        mfrm = mess.getFrom()
        user = mfrm.getStripped()
        prefix = mfrm.getResource()
        text = misc.force_unicode(mess.getBody())
        if ((not prefix) or (type == 'groupchat' and prefix == self.res) or
            (not text)):
            return

        # Checking command
        if text[0] == '%':
            text = text[1:]
        else:
            if type == 'groupchat':
                url_match = misc.url_re.search(text)
                if url_match is not None:
                    url = url_match.group()
                    title = misc.getTitle(url)
                    if title:
                        self.send(user, type, 'Title: ' + title)
            return

        # Parsing command
        spl = text.split()
        if spl:
            cmd, args = spl[0], spl[1:]
        else:
            return

        if self._inRoom(user):
            owner = prefix == self.owner[1]     # Msg from room
        else:
            owner = user == self.owner[0]       # Msg from jid

        if type == 'groupchat':
            if '>' in args:
                index  = args.index('>')        # Redirect (>)
                prefix = ''
                redir  = ' '.join(args[index+1:])
                if redir:
                    prefix = redir + ', '
                args   = args[:index]
            else:
                prefix += ', '                  # Groupchat => prefix
        else:
            user, prefix = mfrm, ''             # Chat => no prefix

        # Executing command
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
            return #result = 'command not found: %s' %(cmd)

        if self.__finished: return

        if error:
            error = 'MODULE: exception in %s' %(cmd)
            logging.error(error)
            msg, extra = error, ''
        else:
            if result:
                if isinstance(result, tuple):
                    msg, extra = result
                else:
                    msg, extra = result, ''
            else:
                msg, extra = 'invalid syntax', ''

        # Replying
        if msg:
            self.send(user, type, prefix + misc.force_unicode(msg), extra)

    def presenceCB(self, conn, pres):
        if pres.getType() == 'subscribe' and pres.getFrom().getStripped() == self.owner[0]:
            self.conn.send(xmpp.Presence(to=pres.getFrom(), typ='subscribed'))

        if pres.getFrom().getResource() == self.res and pres.getType() == 'unavailable' and pres.getStatus() == 'Replaced by new connection':
            user = pres.getFrom().getStripped()
            for room in self.rooms:
                if user == room[0]:
                    self._join_presence(self.conn, room[0], room[1])

    def iqCB(self, conn, iq_node):
        self.iq = iq_node

    def process(self):
        while not self.__finished:
            try:
                self.checkReconnect()

                if self.conn:
                    self.conn.Process(1)
                else:
                    if self.connect():
                        logging.info('CONNECTION: bot connected')
                    else:
                        time.sleep(self.reconnectTime)
            except xmpp.protocol.XMLNotWellFormed:
                logging.error('CONNECTION: reconnect (detected not valid XML)')
                self.conn = None
            except KeyboardInterrupt:
                self.exit('EXIT: interrupted by keyboard')
            except SystemExit:
                self.exit('EXIT: interrupted by SIGTERM')
            except ReloadData:
                logging.info('RELOAD: by SIGHUP')
                self.load()

    def checkReconnect(self):
        if self.conn:
            now = datetime.datetime.now()
            if (now - self.last).seconds > self.reconnectTime:
                if self.iq:
                    self.iq = None
                    self.last = now
                    self.conn.send(xmpp.protocol.Iq(to='jabber.ru', typ='get', queryNS=xmpp.NS_TIME))
                else:
                    logging.warning('CONNECTION: reconnect (iq reply timeout)')
                    self.conn = None
                    self.iq = True


def sigTermCB(signum, frame):
    raise SystemExit()


class ReloadData(Exception):
    pass


def sigHupCB(signum, frame):
    raise ReloadData()
