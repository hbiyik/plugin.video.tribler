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


class index(container.Contianer):
    def subbed(self):
        js = rest.jsquery("channels", "subscribed")

        for channel_info in js.get("subscribed", []):
            name = channel_info.get('name')
            channel_id = channel_info.get('dispersy_cid')
            self.item(name, method="show").dir(channel_id, name)

    def popular(self):
        for channel_info in rest.jsquery("channels", "popular").get("channels"):
            name = channel_info.get('name')
            channel_id = channel_info.get('dispersy_cid')
            self.item(name, method="show").dir(channel_id, name)

    def show(self, channel_id, cname):
        js = rest.jsquery("channels", "discovered", channel_id, "torrents")
        for _ in torrent.iterate(self, js.get("torrents", [])):
            pass
