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
from tinyxbmc import addon
from tinyxbmc import gui

from plugin import util
from plugin import const
from plugin import rest
from plugin import setting

import urllib

stng = setting.Setting()


def magnet(ihash, name=""):
    return ('magnet:?xt=urn:btih:%s&dn=%s' % (ihash, name)).encode('utf-8')


def add_download(ihash, name="", anond=None, anonu=None):
    destination = stng.download_direction
    if stng.ask_download_settings:
        destination = gui.browse(3, addon.local(33008), 'files', '', default=destination)

    m = urllib.quote(magnet(ihash, name))
    if not anond:
        anond = stng.anond
    if not anonu:
        anonu = stng.anonu
    data = {
            "anon_hops": anond,
            "safe_seeding": anonu,
            "destination": destination,
            "uri": m
            }
    js, response = rest.jsput("downloads", **data)
    status = response.status_code
    if status == 200:
        gui.notify(name, 'Download started')
    elif 'error' in js:
        if "message" in js["error"]:
            gui.warn(name, js["error"]["message"])
        else:
            gui.warn(name, js["error"])
    else:
        gui.error('ERROR', 'Failed to start download')


def _patch_download(ihash, state=None, files=[], hops=None):
    data = {}
    if state:
        data["state"] = state
    if len(files):
        pass
    if hops:
        data["anon_hops"] = hops
    js, response = rest.jspatch("download", ihash, **data)
    status = response.status_code
    if status == 200:
        gui.notify(ihash, 'Download Updated')
    elif "error" in js:
        gui.warn(ihash, js["error"])
    else:
        gui.error('ERROR', 'Failed to change download')


def stop_download(ihash):
    return _patch_download(ihash, state="stop")


def start_download(ihash):
    return _patch_download(ihash, state="resume")


def recheck_download(ihash):
    return _patch_download(ihash, state="recheck")


def set_download_anonimity(ihash, hops=0):
    return _patch_download(ihash, hops=hops)


def remove_download(ihash):
    pass


def iterate(cntx, torrents):
    for tinfo in torrents:
        name = tinfo.get('name')
        if name == 'Unknown name' or name == 'Unnamed torrent':
            continue
        title = name
        status = tinfo.get("status")
        if status:
            title = "[%s] %s" % (const.DLSTATUS[status], title)
        seed = tinfo.get("num_seeders", 0)
        if seed:
            title += " S:%d" % seed
        leech = tinfo.get("num_leechers", 0)
        if leech:
            title += " L:%d" % leech
        # to-do: make this human readable
        fsize = tinfo.get("size", 0)
        if fsize:
            title += " F:%sB" % util.humanbyte(fsize)
        d = cntx.item(title)
        d.module = "containers.torrents"
        d.container = "index"
        d.method = "process"
        d.call(tinfo.get("infohash"))
        yield d, tinfo
