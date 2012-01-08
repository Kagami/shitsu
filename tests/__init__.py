try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestModule(unittest.TestCase):
    """Helper class for testing cc's modules."""

    module_name = None

    def setUp(self):
        class_name = self.__class__.__name__
        if self.module_name is None:
            self.module_name = class_name.lower()
        mod = __import__("shitsu.modules." + self.module_name)
        mod = getattr(mod.modules, self.module_name)
        self._module = getattr(mod, class_name)(None)

    def run_m(self, *args, **kwargs):
        return self._module.run(*args, **kwargs)
