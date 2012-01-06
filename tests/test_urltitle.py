# coding: utf-8

import tests


class Urltitle(tests.TestModule):

    def test_private(self):
        self.assertEqual(
            self.run_m("http://localhost/"),
            "")

    def test_windows1251(self):
        self.assertEqual(
            self.run_m("http://www.yermak.com.ua/txt/pol/art_kursk.html"),
            u'Title: "Курск" все-таки торпедировали американские военно-морские силы.')

    def test_windpws1251(self):
        self.assertEqual(
            self.run_m("http://atv.odessa.ua/?t=11803"),
            u"Title: Coca-Cola — яд XXI-го века - Взгляд с Виктором Орлом - программы АТВ | Одесса, Украина")

    def test_header(self):
        self.assertEqual(
            self.run_m("http://ya.ru/"),
            u"Title: Яндекс")

    def test_youtube(self):
        self.assertEqual(
            self.run_m("http://www.youtube.com/watch?v=ZjFIt78fCxI"),
            u"Title: 【東方Vocal】【東方地霊殿】EastNewSound - Sadistic Paranoia with English Subtitles - YouTube")

    def test_koi8r(self):
        self.assertEqual(
            self.run_m("http://www.gnu.org/philosophy/right-to-read.ru.html"),
            u"Title: Право читать (The Right To Read) - Проект GNU - Фонд Свободного ПО (FSF)")

    def test_htmlentities(self):
        self.assertEqual(
            self.run_m("http://iichan.ru/b/"),
            u"Title: IIchan.ru — Бред")

    def test_longtitle(self):
        self.assertEqual(
            self.run_m("http://gelbooru.com/index.php?page=post&s=view&id=1386757"),
            u"Title: Gelbooru- 1girl blush book bow breasts capelet cleavage crescent desk dress from above furukawa lemon hair bow hair ribbon hat large breasts long hair…")

    def test_idna(self):
        self.assertEqual(
            self.run_m(u"http://тохо.рф/"),
            u"Title: НЯШКИ ТУТ!")

    def test_timeout(self):
        self.assertEqual(
            self.run_m("https://ya.ru/"),
            "")
