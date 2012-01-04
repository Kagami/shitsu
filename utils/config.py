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
            self._opts[section] = dict(self._config.items(section))

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
