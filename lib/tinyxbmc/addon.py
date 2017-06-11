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

import traceback


def get_addon(addon_name=""):
    try:
        a = xbmcaddon.Addon(addon_name)
    except RuntimeError:
        try:
            a = xbmcaddon.Addon()
        except RuntimeError:
            a = None
    return a


def get_profile(addon_name=""):
    a = get_addon(addon_name)
    if a:
        profile = a.getAddonInfo('profile')
        return xbmc.translatePath(profile).decode("utf-8")
    else:
        return a


class setting():
    def __init__(self, name=""):
        self.e = "utf-8"
        self.profile = get_profile(name)
        self.a = get_addon(name)

    @staticmethod
    def ischanged(name=""):
        f = os.path.join(get_profile(name), "settings.xml")
        if os.path.exists(f):
            cur_s = str(os.path.getsize(f))
        else:
            cur_s = "-1"
        f = os.path.join(get_profile(name), "settings.size")
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
        return bool(self.a.getSetting(variable) == 'true')

    def getstr(self, variable):
        return str(self.a.getSetting(variable).decode(self.e))

    def getint(self, variable):
        val = self.a.getSetting(variable)
        if isinstance(val, (int, float)):
            return int(val)
        elif isinstance(val, (str, unicode)) and val.isdigit():
            return int(val)
        else:
            return -1

    def getfloat(self, variable):
        return float(self.a.getSetting(variable))

    def set(self, key, value):
        if isinstance(value, bool):
            value = str(value).lower()
        elif not isinstance(value, (str, unicode)):
            value = str(value)
        return self.a.setSetting(key, value)


def local(sid, addon_name=""):
    a = get_addon(addon_name)
    if a:
        return a.getLocalizedString(sid).encode('utf-8')
    else:
        return xbmc.getLocalizedString(sid)


class blockingloop(object):
    def __init__(self, *args, **kwargs):
        self.wait = 0.1
        self.__terminate = False
        self.init(*args, **kwargs)
        self.oninit()
        e = None
        self.__mon = None
        try:
            self.__mon = xbmc.Monitor()
            while not self.isclosed():
                try:
                    self.onloop()
                except Exception, e:
                    traceback.print_exc()
                    break
                if self.__mon.waitForAbort(self.wait) or self.isclosed():
                    if not self.__terminate:
                        self.onclose()
                    break
            del self.__mon
        except AttributeError:
            while True:
                try:
                    self.onloop()
                except Exception, e:
                    traceback.print_exc()
                    break
                if not self.isclosed():
                    if not self.__terminate:
                        self.onclose()
                xbmc.sleep(int(self.wait * 1000))
        if e:
            raise(e)

    def init(self, *args, **kwargs):
        pass

    def oninit(self):
        pass

    def onloop(self):
        pass

    def onclose(self):
        pass

    def isclosed(self):
        if self.__mon:
            return self.__mon.abortRequested() or self.__terminate
        else:
            return xbmc.abortRequested or self.__terminate

    def close(self):
        self.onclose()
        self.__terminate = True
