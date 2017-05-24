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
import os

a = xbmcaddon.Addon()
addonid = a.getAddonInfo('id')
profile = a.getAddonInfo('profile')
profile = xbmc.translatePath(profile).decode("utf-8")


class setting():
    def __init__(self):
        self.e = "utf-8"

    @staticmethod
    def ischanged():
        f = os.path.join(profile, "settings.xml")
        if os.path.exists(f):
            cur_s = str(os.path.getsize(f))
        else:
            cur_s = "-1"
        f = os.path.join(profile, "settings.size")
        if os.path.exists(f):
            with open(f, "r") as sfile:
                pre_s = sfile.read()
        else:
            pre_s = "-1"
        if cur_s == pre_s:
            return False
        else:
            with open(f, "w") as sfile:
                sfile.write(cur_s)
            return True

    def getbool(self, variable):
        return bool(a.getSetting(variable) == 'true')

    def getstr(self, variable):
        return str(a.getSetting(variable).decode(self.e))

    def getint(self, variable):
        val = a.getSetting(variable)
        if isinstance(val, (int, float)):
            return int(val)
        elif isinstance(val, (str, unicode)) and val.isdigit():
            return int(val)
        else:
            return -1

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


class blockingloop(object):
    def __init__(self, *args, **kwargs):
        self.wait = 0.1
        self.init(*args, **kwargs)
        self.onstart()
        try:
            mon = xbmc.Monitor()
            while not (mon.abortRequested() or self.isclosed()):
                self.onloop()
                if mon.waitForAbort(self.wait) or self.isclosed():
                    break
        except AttributeError:
            while not (xbmc.abortRequested or self.isclosed()):
                self.onloop()
                xbmc.sleep(self.wait * 1000)
        self.onclose()

    def init(self, *args, **kwargs):
        pass

    def onstart(self):
        pass

    def onloop(self):
        pass

    def onclose(self):
        pass

    def isclosed(self):
        return False
