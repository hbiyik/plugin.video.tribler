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
from tinyxbmc import gui

from plugin import rest
from plugin import torrent


class index(container.Contianer):
    def iterate(self, channels):
        for cinfo in channels:
            name = cinfo.get('name')
            cid = cinfo.get('dispersy_cid')
            subbed = cinfo.get("subscribed")
            if subbed:
                cntx = self.item(addon.local(33002), method="unsub")
            else:
                cntx = self.item(addon.local(33001), method="sub")
            d = self.item(name, method="show")
            d.context(cntx, False, cid, name)
            d.removeold = True
            yield d, cinfo

    def sub(self, cid, cname=None):
        if not cname:
            cname = cid
        js, response = rest.jsput("channels", "subscribed", cid)
        status = response.status_code
        if status == 409:
            gui.warn(cname, "Not a subscribed channel")
        else:
            gui.notify(cname, "Subscribed")
        self._update(0)

    def unsub(self, cid, cname=None):
        if not cname:
            cname = cid
        js, response = rest.jsdel("channels", "subscribed", cid)
        status = response.status_code
        if status == 404:
            gui.warn(cname, "Already subscribed")
        else:
            gui.notify(cname, "Un-subscribed")
        self._update(0)

    def subbed(self):
        js = rest.jsquery("channels", "subscribed")
        for d, cinfo in self.iterate(js.get("subscribed", [])):
            d.dir(cinfo.get('dispersy_cid'), cinfo.get("name"))

    def popular(self):
        js = rest.jsquery("channels", "popular")
        for d, cinfo in self.iterate(js.get("channels", [])):
            d.dir(cinfo.get('dispersy_cid'), cinfo.get("name"))

    def discovered(self):
        js = rest.jsquery("channels", "discovered")
        for d, cinfo in self.iterate(js.get("channels", [])):
            d.dir(cinfo.get('dispersy_cid'), cinfo.get("name"))

    def show(self, channel_id, cname):
        js = rest.jsquery("channels", "discovered", channel_id, "torrents")
        for _ in torrent.iterate(self, js.get("torrents", [])):
            pass
