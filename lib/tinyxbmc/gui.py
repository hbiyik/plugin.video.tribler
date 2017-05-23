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
import xbmcgui
import os
import math

from tinyxbmc import addon


__artdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
_white = os.path.join(__artdir, "white.png")
_gray = os.path.join(__artdir, "gray.png")
_black = os.path.join(__artdir, "black.png")
_red = os.path.join(__artdir, "red.png")


def browse(typ, heading, shares, mask="", useThumbs=True, treatAsFolder=True,
           default="", enableMultiple=False):
    '''
    Types:
    - 0 : ShowAndGetDirectory
    - 1 : ShowAndGetFile
    - 2 : ShowAndGetImage
    - 3 : ShowAndGetWriteableDirectory
    '''
    dialog = xbmcgui.Dialog()
    return dialog.browse(typ, heading, shares, mask, useThumbs, treatAsFolder,
                         default, enableMultiple)


def notify(title, content, typ=None):
    if not typ:
        typ = xbmcgui.NOTIFICATION_INFO
    dialog = xbmcgui.Dialog()
    dialog.notification(title, content, typ)


def warn(title, content):
    notify(content, xbmcgui.NOTIFICATION_WARNING)


def error(title, content):
    notify(content, xbmcgui.NOTIFICATION_ERROR)


def progress(name):
    dialog = xbmcgui.DialogProgress()
    dialog.create(name)
    return dialog


class form(xbmcgui.WindowDialog):
    def __init__(self, w1, w2, header=""):
        xbmcgui.WindowDialog.__init__(self)
        self.setCoordinateResolution(0)
        #  1920x1080
        self.__cw = 1920
        self.__ch = 1080
        self.__w1 = w1
        self.__w2 = w2
        self.__padx = 25
        self.__rowh = 43  # changes depending on the selected skin :(
        self.__pady = self.__padx - 10
        self.__elems = {}
        self.__cmap = {}
        self.__eid = 0
        self.__numbtns = 0
        self.__calls = {
                "text": ("setLabel", "getLabel", []),
                "edit": ("setText", "getText", []),
                "bool": ("setSelected", "getSelected", []),
                "button": ("setLabel", "getLabel", []),
                }
        self.init()
        self.__terminate = False
        self.__pre = None
        self.__create(header)
        self.show()
        #  prevent kodi gc to work properly using singular inheritance
        addon.blockingloop.isclosed = self.isclosed
        addon.blockingloop.onclose = self.onclose
        addon.blockingloop.onloop = self.onloop
        addon.blockingloop()

    def __pos(self, eid, x, y, w, h):
        elem = self.getelem(eid)
        elem.setPosition(x, y)
        elem.setWidth(w)
        elem.setHeight(h)
        self.addControl(elem)
        self.__cmap[elem.getId()] = eid
        if self.__pre:
            self.__pre.controlDown(elem)
            self.__pre.controlRight(elem)
            elem.controlUp(self.__pre)
            elem.controlLeft(self.__pre)
        else:
            self.setFocus(elem)
        self.__pre = elem
        return elem

    def __row(self, eid, rx, y, label):
        self.addControl(xbmcgui.ControlLabel(rx, y, self.__w1, self.__rowh,
                                             label))
        self.__pos(eid, rx + self.__w1, y, self.__w2, self.__rowh)
        return y + self.__rowh + self.__pady

    def __create(self, header):
        h = 0
        w = self.__w1 + self.__w2
        bw = minbuttonw = (w - self.__padx * 2) / 3
        for eid, elem in self.__elems.iteritems():
            if not elem[0] == "button":
                h += self.__rowh + self.__pady
        bsize = int(w / minbuttonw)
        h += int(math.ceil(float(self.__numbtns) / bsize) *
                 (self.__rowh + self.__pady))  # ;) math porn
        h -= self.__pady
        x = rx = (self.__cw - w) / 2
        y = ry = (self.__ch - h) / 2
        self.addControl(xbmcgui.ControlImage(
                                             rx - self.__padx,
                                             ry - self.__pady - self.__rowh,
                                             w + 2 * self.__padx,
                                             self.__rowh,
                                             _red
                                             )
                        )
        self.addControl(xbmcgui.ControlLabel(
                                             rx,
                                             ry - self.__pady - self.__rowh,
                                             w + 2 * self.__padx,
                                             self.__rowh,
                                             header,
                                             )
                        )
        self.addControl(xbmcgui.ControlImage(
                                             rx - self.__padx,
                                             ry - self.__pady,
                                             w + 2 * self.__padx,
                                             h + 2 * self.__pady,
                                             _black
                                             )
                        )

        for eid, (typ, label, clck, fcs, elem) in self.__elems.iteritems():
            if typ == "edit":
                y = self.__row(eid, rx, y, label)
            if typ == "text":
                y = self.__row(eid, rx, y, label)
            if typ == "bool":
                y = self.__row(eid, rx, y, label)
            if typ == "progress":
                self.addControl(xbmcgui.ControlImage(rx, y, w, self.__rowh, _gray))
                self.__pos(eid, rx, y, 0, self.__rowh)
                y += self.__rowh + self.__pady
        numbtns = 0
        for eid, (typ, label, clck, fcs, elem) in self.__elems.iteritems():
            if typ == "button":
                if minbuttonw * self.__numbtns + self.__padx * (self.__numbtns - 1) < w:
                    bw = (w - (self.__numbtns - 1) * self.__padx) / self.__numbtns
                else:
                    bw = (w - (bsize - 1) * self.__padx) / bsize
                self.__pos(eid, x, y, bw, self.__rowh)
                x += bw + self.__padx
                numbtns += 1
                if x + minbuttonw > rx + w:
                    x = rx
                    y += self.__rowh + self.__pady
                    self.__numbtns -= numbtns
                    numbtns = 0

    @staticmethod
    def __null(*args, **kwargs):
        pass

    def getelem(self, eid):
        return self.__elems[eid][-1]

    def get(self, eid):
        typ, lbl, clck, fcs, elem = self.__elems[eid]
        if typ == "progress":
            return elem.getWidth() * 100 / (self.__w1 + self.__w2)
        else:
            setter, getter, args = self.__calls[typ]
            return getattr(elem, getter)(*args)

    def set(self, eid, value):
        typ, lbl, clck, fcs, elem = self.__elems[eid]
        if typ == "progress":
            elem.setWidth(value * (self.__w1 + self.__w2) / 100)
        else:
            setter, getter, args = self.__calls[typ]
            getattr(elem, setter)(value)

    def text(self, label="", value=""):
        elem = xbmcgui.ControlLabel(0, 0, 0, 0, value)
        self.__eid += 1
        self.__elems[self.__eid] = ("text", label, self.__null, self.__null, elem)
        return self.__eid

    def edit(self, label="", default=""):
        elem = xbmcgui.ControlEdit(0, 0, 0, 0, default)
        self.__eid += 1
        self.__elems[self.__eid] = ("edit", label, self.__null, self.__null, elem)
        return self.__eid

    def bool(self, label="", onclick=None):
        if not onclick:
            onclick = self.__null
        elem = xbmcgui.ControlCheckMark(0, 0, 0, 0, "",
                                        focusTexture=_red,
                                        noFocusTexture=_white
                                        )
        self.__eid += 1
        self.__elems[self.__eid] = ("bool", label, onclick, self.__null, elem)
        return self.__eid

    def button(self, label="", onclick=None):
        if not onclick:
            onclick = self.__null
        elem = xbmcgui.ControlButton(0, 0, 0, 0, label)
        self.__eid += 1
        self.__elems[self.__eid] = ("button", label, onclick, self.__null, elem)
        self.__numbtns += 1
        return self.__eid

    def progress(self, label=""):
        elem = xbmcgui.ControlImage(0, 0, 0, 0, _white)
        self.__eid += 1
        self.__elems[self.__eid] = ("progress", label, self.__null, self.__null, elem)
        return self.__eid

    def onAction(self, action):
        if action in [
                      xbmcgui.ACTION_PREVIOUS_MENU,
                      xbmcgui.ACTION_NAV_BACK
                      ]:
            self.onclose()

    def onFocus(self, controlId):
        pass

    def onControl(self, ctrl):
        eid = self.__cmap.get(ctrl.getId())
        if eid:
            typ, lbl, clck, fcs, elem = self.__elems[eid]
            clck()

    def isclosed(self):
        return self.__terminate

    def onclose(self):
        self.close()
        self.__terminate = True

    def onloop(self):
        pass
