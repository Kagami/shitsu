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

# coding: utf-8

import tests


class Port(tests.TestModule):

    module_name = "nmap"

    def test_private(self):
        self.assertIsNone(self.run_m("127.0.0.1", "80"))
        self.assertIsNone(self.run_m("127.3.3.1", "80"))
        self.assertIsNone(self.run_m("192.168.1.5", "80"))
        self.assertIsNone(self.run_m(u"172.17.1.3", "80"))
        self.assertIsNone(self.run_m(u"172.16.0.0", "80"))
        self.assertIsNone(self.run_m("localhost", "80"))
        self.assertIsNone(self.run_m("localhost.localdomain", "80"))

    def test_port(self):
        self.assertIsNone(self.run_m("ya.ru", "0"))
        self.assertIsNone(self.run_m("ya.ru", "65536"))
        self.assertIsNone(self.run_m("ya.ru", "-10"))
        self.assertIsNone(self.run_m("ya.ru", "nenyak"))
        self.assertIsNone(self.run_m("ya.ru", "80k"))

    def test_ok(self):
        self.assertIsNotNone(self.run_m("ya.ru", "80"))

    def test_idna(self):
        self.assertIsNotNone(self.run_m(u"тохо.рф", "80"))

    def test_badhost(self):
        self.assertIsNone(self.run_m("nyak..ru", "80"))
        self.assertIsNone(self.run_m("_nyak.ru", "80"))
        self.assertIsNone(self.run_m("nyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyakn.ru", "80"))
        self.assertIsNone(self.run_m("nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.ru", "80"))


class Nmap(tests.TestModule):

    def test_private(self):
        self.assertIsNone(self.run_m("127.0.0.1"))
        self.assertIsNone(self.run_m("127.3.3.1"))
        self.assertIsNone(self.run_m("192.168.1.5"))
        self.assertIsNone(self.run_m(u"172.17.1.3"))
        self.assertIsNone(self.run_m(u"172.16.0.0"))
        self.assertIsNone(self.run_m("localhost"))
        self.assertIsNone(self.run_m("localhost.localdomain"))

    def test_badhost(self):
        self.assertIsNone(self.run_m("nyak..ru"))
        self.assertIsNone(self.run_m("_nyak.ru"))
        self.assertIsNone(self.run_m("nyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyaknyakn.ru"))
        self.assertIsNone(self.run_m("nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.nyak.ru"))
