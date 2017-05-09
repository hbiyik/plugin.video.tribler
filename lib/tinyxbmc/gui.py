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


def browse(typ, heading, shares, mask="", useThumbs=True, treatAsFolder=True, \
           default="", enableMultiple=False):
    '''
    Types:
    - 0 : ShowAndGetDirectory
    - 1 : ShowAndGetFile
    - 2 : ShowAndGetImage
    - 3 : ShowAndGetWriteableDirectory
    '''
    dialog = xbmcgui.Dialog()
    return dialog.browse(typ, heading, shares, mask, useThumbs, treatAsFolder, \
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
