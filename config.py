import threading
import ConfigParser


class Config(object):
    """Wrapper around ConfigParser.
    Can create section objects via get_sect,
    get and set options values.
    Set operation is thread-safe.
    """

    filename = "C.C..cfg"

    def __init__(self):
        self._lock = threading.Lock()
        self._config = ConfigParser.RawConfigParser()
        self._config.read(self.filename)
        self._items = {}
        for section in self._config.sections():
            self._items[section] = dict(self._config.items(section))

    def get_sect(self, section):
        return ConfigSection(self, section)

    def get(self, section, option, default=None):
        if section in self._items:
            return self._items[section].get(option, default)
        else:
            return default

    def set(self, section, option, value):
        # Should be thread-safe operation.
        with self._lock:
            if section not in self._items:
                self._items[section] = {}
            self._items[section][option] = value
            self._config.set(section, option, value)
            with open(self.filename, "wb") as f:
                self._config.write(f)


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
