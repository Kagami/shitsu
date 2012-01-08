# coding: utf-8

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

import types
import datetime
from shitsu import utils
import tests


class Urltitle(tests.TestModule):

    def timeout(seconds):
        """Helper decorator for check timeout."""
        def check_timeout(fn):
            def new(self):
                start = datetime.datetime.now()
                fn(self)
                delta = datetime.datetime.now() - start
                max_delta = datetime.timedelta(seconds=seconds)
                if delta > max_delta:
                    self.fail("Elapsed time is %s, but must be "
                              "less than %s." % (delta, max_delta))
            return new
        if type(seconds) is types.FunctionType:
            fn = seconds
            seconds = utils.default_url_timeout + 0.1
            return check_timeout(fn)
        return check_timeout

    @timeout
    def test_private(self):
        self.assertEqual(
            self.run_m("http://localhost/"),
            "")

    @timeout
    def test_windows1251(self):
        self.assertEqual(
            self.run_m("http://www.yermak.com.ua/txt/pol/art_kursk.html"),
            u'Title: "Курск" все-таки торпедировали американские военно-морские силы.')

    @timeout
    def test_windpws1251(self):
        self.assertEqual(
            self.run_m("http://atv.odessa.ua/?t=11803"),
            u"Title: Coca-Cola — яд XXI-го века - Взгляд с Виктором Орлом - программы АТВ | Одесса, Украина")

    @timeout
    def test_koi8r(self):
        self.assertEqual(
            self.run_m("http://www.gnu.org/philosophy/right-to-read.ru.html"),
            u"Title: Право читать (The Right To Read) - Проект GNU - Фонд Свободного ПО (FSF)")

    @timeout
    def test_eucjp(self):
        self.assertEqual(
            self.run_m("http://www.mozilla.gr.jp/standards/webtips0022.html"),
            u"Title: 文字コード宣言は行いましょう(HTML) - Web標準普及プロジェクト")

    @timeout
    def test_header(self):
        self.assertEqual(
            self.run_m("http://ya.ru/"),
            u"Title: Яндекс")

    @timeout
    def test_youtube(self):
        self.assertEqual(
            self.run_m("http://www.youtube.com/watch?v=ZjFIt78fCxI"),
            u"Title: 【東方Vocal】【東方地霊殿】EastNewSound - Sadistic Paranoia with English Subtitles - YouTube")

    @timeout
    def test_htmlentities(self):
        self.assertEqual(
            self.run_m("http://iichan.ru/b/"),
            u"Title: IIchan.ru — Бред")

    @timeout
    def test_longtitle(self):
        self.assertEqual(
            self.run_m("http://gelbooru.com/index.php?page=post&s=view&id=1386757"),
            u"Title: Gelbooru- 1girl blush book bow breasts capelet cleavage crescent desk dress from above furukawa lemon hair bow hair ribbon hat large breasts long hair…")

    @timeout
    def test_idna(self):
        self.assertEqual(
            self.run_m(u"http://тохо.рф/"),
            u"Title: НЯШКИ ТУТ!")

    @timeout
    def test_timeout(self):
        self.assertEqual(
            self.run_m("https://ya.ru/"),
            "")
