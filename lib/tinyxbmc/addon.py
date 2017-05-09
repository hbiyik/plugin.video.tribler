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
import xbmc

a = xbmcaddon.Addon()


class setting():
    def __init__(self):
        self.e = "utf-8"

    def getbool(self, variable):
        return bool(a.getSetting(variable) == 'true')

    def getstr(self, variable):
        return str(a.getSetting(variable).decode(self.e))

    def getint(self, variable):
        return int(a.getSetting(variable))

    def getfloat(self, variable):
        return float(a.getSetting(variable))

    def set(self, key, value):
        if isinstance(value, bool):
            value = str(value).lower()
        elif not isinstance(value, (str, unicode)):
            value = str(value)
        return a.setSetting(key, value)


def local(sid):
    return a.getLocalizedString(sid).encode('utf-8')

addonid = a.getAddonInfo('id')
profile = a.getAddonInfo('profile')
profile = xbmc.translatePath(profile).decode("utf-8")


class blockingloop(object):
    def __init__(self, *args, **kwargs):
        self.wait = 0.1
        self.init(*args, **kwargs)
        try:
            mon = xbmc.Monitor()
            while not (mon.abortRequested() or self.dobreak()):
                self.onloop()
                if mon.waitForAbort(self.wait) or self.dobreak():
                    break
            self.onbreak()
        except AttributeError:
            while not (xbmc.abortRequested or self.dobreak()):
                self.onloop()
                xbmc.sleep(self.wait * 1000)
            self.onbreak()

    def init(self, *args, **kwargs):
        pass

    def onloop(self):
        pass

    def onbreak(self):
        pass

    def dobreak(self):
        return False
