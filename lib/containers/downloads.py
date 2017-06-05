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

from plugin import rest
from plugin import torrent
from plugin import const


class index(container.Contianer):
    def init(self):
        self.autoupdate = const.CONTAINERINTERVAL

    def show(self, *states, **kwargs):
        js = rest.jsget("downloads", get_peers=1, get_pieces=1)[0].get("downloads")
        for d, tinfo in torrent.iterate(self, js):
            tstatus = tinfo.get("status")
            if tstatus in states and not kwargs.get("revert", False):
                continue
