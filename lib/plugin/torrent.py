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

stng = setting.Setting()


def download(ihash, name):
    destination = stng.download_direction
    if stng.ask_download_settings:
        destination = gui.browse(3, addon.local(33008), 'files', '', default=destination)

    magnet = ('magnet:?xt=urn:btih:%s&dn=%s' % (ihash, name)).encode('utf-8')
    data = {
            "anon_hops": stng.anond,
            "safe_seeding": stng.anonu,
            "destination": destination,
            "uri": magnet
            }
    js, response = rest.jsput("downloads", **data)
    status = response.status_code
    if status == 200:
        gui.notify(name, 'Download started')
    elif js.get('error').get('message') == u'This download already exists.':
        gui.warn(name, 'Download already exists')
    else:
        gui.error('ERROR', 'Failed to start download')


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


class ui(addon.blockingloop):
    def init(self, ihash):
        self.wait = const.UIINTERVAL
        self.kprogress = gui.progress("UI")  # to-do: make this prettier
        self.ihash = ihash

    def onloop(self):
        download_list = rest.jsquery("downloads", get_peers=1, get_pieces=1).get("downloads")

        download_info = None
        for download_info in download_list:
            if download_info.get('infohash') == self.ihash:
                break

        progress = download_info.get('progress')
        speed_up = download_info.get('speed_up')
        speed_down = download_info.get('speed_down')
        eta = download_info.get('eta')
        filesize = download_info.get('size')
        seeder = download_info.get('num_seeds')
        leecher = download_info.get('num_peers')
        destination = download_info.get('destination')
        status = download_info.get('status')

        h_eta = '%s:%s' % (addon.local(33109).title(), util.humants(int(eta)))
        progress_bar = int(progress * 100)
        h_up = "%s: %sB/s" % (addon.local(33105).title(), util.humanbyte(speed_up))
        h_down = "%s: %sB/s" % (addon.local(33107).title(), util.humanbyte(speed_down))
        h_seed = "%s: %d" % (addon.local(33104).title(), seeder)
        h_leech = "%s: %d" % (addon.local(33106).title(), leecher)

        progress_dis = "%s: %sB/ %sB, %%%d, %s" % (
                                             addon.local(33101),
                                             util.humanbyte(filesize * progress),
                                             util.humanbyte(filesize),
                                             progress * 100,
                                             h_eta
                                             )
        speed_dis = ", ".join([h_down, h_up, h_seed, h_leech])
        dest_dis = "%s: %s" % (addon.local(33103).title(), destination)

        self.kprogress.update(progress_bar, progress_dis, speed_dis, dest_dis)

    def isclosed(self):
        return self.kprogress.iscanceled()
