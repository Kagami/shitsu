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
