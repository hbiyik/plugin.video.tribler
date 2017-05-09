# -*- coding: utf-8 -*-
'''
    Author    : Huseyin BIYIK <husenbiyik at hotmail>
    Year      : 2016
    License   : GPL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from tinyxbmc import container
from tinyxbmc import addon


class index(container.Contianer):
    def index(self):
        d = self.item(addon.local(32001),
                      module="containers.channels",
                      container="index",
                      method="popular"
                      )
        sub = self.item(addon.local(32011),
                         module="containers.torrents",
                         container="index",
                         method="random"
                         )
        d.context(sub, True)
        d.dir()
        self.item(addon.local(32002), container="discovered").dir()
        self.item(addon.local(32003), method="mychannel").dir()
        self.item(addon.local(32004), container="subscriptions", module="containers.channels").dir()
        d = self.item(addon.local(32005), module="containers.downloads", container="index", method="show")
        d_cntx = {
                  32051: [],
                  32052: [],
                  32053: [],
                  32054: [],
                  32055: [],
                  }
        for sid, args in d_cntx.iteritems():
            dsub = self.item(addon.local(sid), module="containers.downloads", container="index", method="show")
            d.context(dsub, True, *args)
        d.removeold = True
        d.dir()
        self.item(addon.local(32006)).dir(container="search")
        self.item(addon.local(32007)).dir(container="settings")

    def mychannel(self):
        pass
