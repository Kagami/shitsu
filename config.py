import ConfigParser


class Config(object):

    def __init__(self):
        self._config = ConfigParser.RawConfigParser()
        self._config.read("C.C..cfg")
        self._sections = self._config.sections()
        self._items = {}
        for section in self._sections:
            self._items[section] = dict(self._config.items(section))

    def get_sect(self, section):
        return ConfigSection(section, self)

    def get(self, section, option):
        if section in self._sections and option in self._items[section]:
            return self._items[section][option]
        else:
            return None


class ConfigSection(object):

    def __init__(self, section, config):
        self._section = section
        self._config = config

    def __getattr__(self, option):
        return self._config.get(self._section, option)
