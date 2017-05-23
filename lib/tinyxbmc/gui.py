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
        self._cw = 1920
        self._ch = 1080
        self._w1 = w1
        self._w2 = w2
        self._padx = 25
        self._texth = 43  # changes depending on the selected skin :(
        self._pady = self._padx - 10
        self._elems = []
        self._numbtns = 0
        self.init()
        self.__calls = {
                "text": ("setLabel", "getLabel", []),
                "edit": ("setText", "getText", []),
                "bool": ("setSelected", "getSelected", []),
                "button": ("setLabel", "getLabel", []),
                }
        self.__terminate = False
        self.__create(header)
        self.show()
        #  prevent kodi gc to work properly using singular inheritance
        addon.blockingloop.isclosed = self.isclosed
        addon.blockingloop.onclose = self.onclose
        addon.blockingloop.onloop = self.onloop
        addon.blockingloop()

    def __pos(self, name, x, y, w, h, suffix=""):
        elem = getattr(self, "_control%s_%s" % (suffix, name))
        elem.setPosition(x, y)
        elem.setWidth(w)
        elem.setHeight(h)
        return elem

    def __row(self, rx, y, name, rlabel, **kwargs):
        self.addControl(xbmcgui.ControlLabel(rx, y, self._w1, self._texth,
                                             rlabel))
        self.addControl(self.__pos(name, rx + self._w1, y, self._w2,
                                   self._texth))
        return y + self._texth + self._pady

    def __create(self, header):
        h = 0
        w = self._w1 + self._w2
        bw = minbuttonw = (w - self._padx * 2) / 3
        for elem in self._elems:
            if not elem[0] == "button":
                h += self._texth + self._pady
        bsize = int(w / minbuttonw)
        h += int(math.ceil(float(self._numbtns) / bsize) *
                 (self._texth + self._pady))  # ;) math porn
        h -= self._pady
        x = rx = (self._cw - w) / 2
        y = ry = (self._ch - h) / 2
        self.addControl(xbmcgui.ControlImage(
                                             rx - self._padx,
                                             ry - self._pady - self._texth,
                                             w + 2 * self._padx,
                                             self._texth,
                                             _red
                                             )
                        )
        self.addControl(xbmcgui.ControlLabel(
                                             rx,
                                             ry - self._pady - self._texth,
                                             w + 2 * self._padx,
                                             self._texth,
                                             header,
                                             )
                        )
        self.addControl(xbmcgui.ControlImage(
                                             rx - self._padx,
                                             ry - self._pady,
                                             w + 2 * self._padx,
                                             h + 2 * self._pady,
                                             _black
                                             )
                        )

        for typ, name, label, kwargs in self._elems:
            kwargs["label"] = label
            if typ == "edit":
                y = self.__row(rx, y, name, label, **kwargs)
            if typ == "text":
                y = self.__row(rx, y, name, label, **kwargs)
            if typ == "bool":
                y = self.__row(rx, y, name, label, **kwargs)
            if typ == "progress":
                self.addControl(self.__pos(name, rx, y, w, self._texth, "bg"))
                self.addControl(self.__pos(name, rx, y, 0, self._texth))
                y += self._texth + self._pady
        numbtns = 0
        for typ, name, label, onclick in self._elems:
            if typ == "button":
                if minbuttonw * self._numbtns + self._padx * (self._numbtns - 1) < w:
                    bw = (w - (self._numbtns - 1) * self._padx) / self._numbtns
                else:
                    bw = (w - (bsize - 1) * self._padx) / bsize
                self.addControl(self.__pos(name, x, y, bw, self._texth))
                x += bw + self._padx
                numbtns += 1
                if x + minbuttonw > rx + w:
                    x = rx
                    y += self._texth + self._pady
                    self._numbtns -= numbtns
                    numbtns = 0

    def get(self, name):
        for typ, ename, label, kwargs in self._elems:
            if name == ename:
                break
        elem = getattr(self, "_control_%s" % name)
        if typ == "progress":
            return elem.getWidth() * 100 / (self._w1 + self._w2)
        else:
            setter, getter, args = self.__calls[typ]
            return getattr(elem, getter)(*args)

    def set(self, name, value):
        for typ, ename, label, kwargs in self._elems:
            if name == ename:
                break
        elem = getattr(self, "_control_%s" % name)
        if typ == "progress":
            elem.setWidth(value * (self._w1 + self._w2) / 100)
        else:
            setter, getter, args = self.__calls[typ]
            getattr(elem, setter)(value)

    def text(self, name, label):
        elem = xbmcgui.ControlLabel(0, 0, 0, 0, "")
        setattr(self, "_control_%s" % name, elem)
        self._elems.append(("text", name, label, {}))
        return elem

    def edit(self, name, label):
        elem = xbmcgui.ControlEdit(0, 0, 0, 0, "")
        setattr(self, "_control_%s" % name, elem)
        self._elems.append(("edit", name, label, {}))
        return elem

    def bool(self, name, label):
        elem = xbmcgui.ControlCheckMark(0, 0, 0, 0, "",
                                        focusTexture=_red,
                                        noFocusTexture=_white
                                        )
        setattr(self, "_control_%s" % name, elem)
        self._elems.append(("bool", name, label, {}))
        return elem

    def button(self, name, label, onclick):
        elem = xbmcgui.ControlButton(0, 0, 0, 0, label)
        setattr(self, "_control_%s" % name, elem)
        self._elems.append(("button", name, label, {"onclick": onclick}))
        self._numbtns += 1
        return elem

    def progress(self, name, label):
        elem = xbmcgui.ControlImage(0, 0, 0, 0, _white)
        elembg = xbmcgui.ControlImage(0, 0, 0, 0, _gray)
        setattr(self, "_control_%s" % name, elem)
        setattr(self, "_controlbg_%s" % name, elembg)
        self._elems.append(("progress", name, label, {}))
        return elem

    def onAction(self, action):
        if action in [
                      xbmcgui.ACTION_PREVIOUS_MENU,
                      xbmcgui.ACTION_NAV_BACK
                      ]:
            self.onclose()

    def onClick(self, controlId):
        print 7777777
        print xbmcgui.WindowDialog.onClick(self, controlId)
        print controlId

    def onFocus(self, controlId):
        print 66666666
        print xbmcgui.WindowDialog.onFocus(self, controlId)
        print controlId

    def isclosed(self):
        return self.__terminate

    def onclose(self):
        self.close()
        self.__terminate = True

    def onloop(self):
        pass
