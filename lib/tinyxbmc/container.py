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

import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmc

import json
import sys
import importlib
import urllib

_default_method = "index"


def refresh():
    xbmc.executebuiltin("Container.Refresh")


class Contianer(object):
    def __init__(self, *iargs, **ikwargs):
        self.sysaddon = sys.argv[0]
        self.syshandle = int(sys.argv[1])
        serial = sys.argv[2][1:]
        try:
            data = json.loads(urllib.unquote_plus(serial))
        except Exception:
            data = {}
        self._items = []
        self._container = data.get("container", self.__class__.__name__)
        self._module = data.get("module", self.__class__.__module__)
        self._method = data.get("method", _default_method)
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        self._disp_container = self._container
        self._disp_module = self._module
        self._disp_method = self._method
        self.ondispatch()
        if self._disp_module == self.__class__.__module__:
            if self._disp_container == self.__class__.__name__:
                self._container = self
            else:
                self._module = sys.modules[self._disp_module]
                self._container = getattr(self._module, self._disp_container)()
                return
        else:
            self._module = importlib.import_module(self._disp_module)
            self._container = getattr(self._module, self._disp_container)()
            return
        xbmc.log("****** TinyXBMC is Dispatching ******")
        xbmc.log("MODULE    : %s" % self._disp_module)
        xbmc.log("CONTAINER : %s" % self._disp_container)
        xbmc.log("METHOD    : %s" % self._disp_method)
        xbmc.log("ARGUMENTS : %s" % repr(args))
        xbmc.log("KW ARGS   : %s" % repr(kwargs))
        xbmc.log("*************************************")
        self._container.autoupdate = False
        self._container.init(*iargs, **ikwargs)
        self._method = getattr(self._container, self._disp_method)
        ret = self._method(*args, **kwargs)
        itemlen = len(self._container._items)
        if itemlen:
            xbmcplugin.addDirectoryItems(self.syshandle, self._container._items, itemlen)
            xbmcplugin.endOfDirectory(self.syshandle, cacheToDisc=True)
            if self._container.autoupdate:
                d = self.item("Auto Update", method="_update")
                d.run(self._container.autoupdate)
        return ret

    def _update(self, wait):
        xbmc.sleep(wait * 1000)
        refresh()

    def init(self, *args, **kwargs):
        pass

    def item(self, name, info={}, art={}, module=None, container=None, method=None):
        if isinstance(name, int):
            name = xbmcaddon.Addon().getLocalizedString(name).encode('utf-8')
        if not art.get("icon"):
            art["icon"] = "DefaultFolder.png"
        if not art.get("thumb"):
            art["thumb"] = "DefaultFolder.png"
        item = xbmcgui.ListItem(label=name)
        item.setArt(art)
        item.setInfo("videos", info)
        tinyitem = itemfactory(self, item, module, container, method)
        tinyitem.name = name
        tinyitem.info = info
        tinyitem.art = art
        return tinyitem

    def index(self, *args, **kwargs):
        item = self.dir("Hello TinyXBMC")
        item.call()
        pass

    def ondispatch(self):
        pass


class itemfactory(object):
    def __init__(self, context, item, module=None, container=None, method=None):
        self._cntx = context
        self.item = item
        if not module:
            module = self._cntx._disp_module
        if not container:
            container = self._cntx._disp_container
        if not method:
            method = self._cntx._disp_method
        self.module = module
        self.container = container
        self.method = method
        self.removeold = False
        self._contexts = []

    def dourl(self, *args, **kwargs):
        data = {
              "module": self.module,
              "container": self.container,
              "method": self.method,
              "args": args,
              "kwargs": kwargs
              }
        serial = urllib.quote_plus(json.dumps(data))
        self.url = '%s?%s' % (self._cntx.sysaddon, serial)
        return self.url

    def _dir(self, isFolder, *args, **kwargs):
        url = self.dourl(*args, **kwargs)
        self.item.addContextMenuItems(self._contexts, self.removeold)
        self._cntx._container._items.append([url, self.item, isFolder])

    def dir(self, *args, **kwargs):
        #  item is added to container as a navigatable folder (isFolder=True)
        self._dir(True, *args, **kwargs)

    def call(self, *args, **kwargs):
        #  item is added to container as a callable folder (isFolder=False)
        self._dir(False, *args, **kwargs)

    def run(self, *args, **kwargs):
        #  item is not added to container but called on runtime
        url = self.dourl(*args, **kwargs)
        xbmc.executebuiltin('RunPlugin(%s)' % url)

    def context(self, sub, isdir, *args, **kwargs):
        url = sub.dourl(*args, **kwargs)
        sub.item.addContextMenuItems(sub._contexts)  # nested fun :)
        if isdir:
            self._contexts.append([sub.name, 'Container.Update(%s)' % url])
        else:
            self._contexts.append([sub.name, 'RunPlugin(%s)' % url])
