import sys
import logging
import threading
import ConfigParser


class Config(object):
    """Wrapper around ConfigParser.
    Can create section objects via get_sect,
    get, set and remove options values.
    """

    filename = "cc.cfg"

    def __init__(self):
        self._lock = threading.Lock()
        self._config = ConfigParser.RawConfigParser()
        self._config.read(self.filename)
        self._opts = {}
        for section in self._config.sections():
            items = {}
            for k, v in self._config.items(section):
                items[k.decode("utf-8")] = v.decode("utf-8")
            self._opts[section] = items
        self._check_config()

    def _check_config(self):
        if not "main" in self._opts:
            self._fail("No main section! Has you set up config?")
        main = self._opts["main"]
        if not "jid" in main:
            self._fail("jid hasn't specified!")
        if not "password" in main:
            self._fail("password hasn't specified!")

    def _fail(self, error):
        logging.critical("CONFIG: %s" % error)
        sys.exit(1)

    def get_sect(self, section):
        return ConfigSection(self, section)

    def get(self, section, option, default=None):
        if section in self._opts:
            return self._opts[section].get(option, default)
        else:
            return default

    def set(self, section, option, value):
        # Should be thread-safe operation.
        with self._lock:
            option = option.encode("utf-8")
            value = value.encode("utf-8")
            if section not in self._opts:
                self._opts[section] = {}
                self._config.add_section(section)
            self._opts[section][option] = value
            self._config.set(section, option, value)
            with open(self.filename, "wb") as f:
                self._config.write(f)

    def remove(self, section, option):
        # Should be thread-safe operation.
        with self._lock:
            del self._opts[section][option]
            self._config.remove_option(section, option)
            with open(self.filename, "wb") as f:
                self._config.write(f)

    def items(self, section):
        if section in self._opts:
            return self._opts[section].items()
        else:
            return []


class ConfigSection(object):
    """Section object.
    Offer access to specified config section.
    """

    def __init__(self, config, section):
        self._config = config
        self._section = section

    def get(self, option, default=None):
        return self._config.get(self._section, option, default)

    def __getattr__(self, option):
        return self._config.get(self._section, option, "")

    def set(self, option, value):
        self._config.set(self._section, option, value)

    def remove(self, option):
        self._config.remove(self._section, option)

    def items(self):
        return self._config.items(self._section)
