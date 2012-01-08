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
