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

from shitsu import xmpp
from shitsu import modules


class Showimage(modules.MessageModule):

    args = (1,)

    def run(self, img_url):
        """<img_url>
        Show img via xhtml-im.
        http://xmpp.org/extensions/xep-0071.html#profile-image
        """
        img = xmpp.Node("img", attrs={"alt": "img", "src": img_url})
        return "<enable xhtml-im to see image>", "<br />" + unicode(img)
