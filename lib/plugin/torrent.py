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
from tinyxbmc import container

from plugin import util
from plugin import const
from plugin import rest
from plugin import setting

import time

stng = setting.Setting()


def magnet(ihash, name=""):
    return ('magnet:?xt=urn:btih:%s&dn=%s' % (ihash, name)).encode('utf-8')


def add_download(ihash, name="", anond=None, anonu=None):
    destination = stng.download_direction
    if stng.ask_download_settings:
        destination = gui.browse(3, addon.local(33008), 'files', '', default=destination)

    m = magnet(ihash, name)
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
    elif js.get('error').get('message') == u'This download already exists.':
        gui.warn(name, 'Download already exists')
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


class ui(gui.form):
    def init(self, ihash):
        self.wait = const.UIINTERVAL
        self.ihash = ihash
        self.state = None
        self.download = None
        self.name = self.label("Name", "")
        self.seeds = self.label(addon.local(33104).title(), "0")
        self.leechs = self.label(addon.local(33106).title(), "0")
        self.fs = self.label("Size", "")
        self.status = self.label("Status")
        self.btn_stream = self.button("Stream", self.on_btn_stream)
        self.btn_add = self.button("Add to Downloads", self.on_btn_add)
        self.btn_download = self.button("Start Download", self.on_btn_download)
        self.btn_files = self.button("View Files", self.on_btn_files)
        self.btn_network = self.button("Query Network", self.on_btn_network)
        self.btn_close = self.button("Close", self.close)
        self.update_btns()

    def oninit(self):
        #  self.querydownload()
        gui.form.oninit(self)
        self.querycache()
        self.update_ui()
        self.hash = hash(repr(self.info))

    def update_ui(self):
        self.set(self.status, self.info["info"]["status"])
        self.set(self.name, self.info["info"]["name"])
        self.set(self.fs, util.humanbyte(self.info["info"]["size"]))
        self.set(self.seeds, str(self.info["info"]["num_seeders"]))
        self.set(self.leechs, str(self.info["info"]["num_leechers"]))
        self.set(self.status, self.info["info"]["status"])

    def update_btns(self):
        if self.getstate() == 0:
            self.enable(self.btn_stream)
            self.set(self.btn_download, "Start Download")
        elif self.getstate() == 1:
            self.enable(self.btn_stream)
            self.set(self.btn_download, "Stop Download")
        elif self.getstate() == 2:
            self.disable(self.btn_stream)
            self.set(self.btn_download, "Stop Streaming")

        if self.isadded():
            self.enable(self.btn_download)
            self.enable(self.btn_stream)
            self.set(self.btn_add, "Remove From Downloads")
        else:
            self.disable(self.btn_download)
            self.disable(self.btn_stream)

    def getstate(self):
        # 0: stopped
        # 1: downloading
        # 2: streaming
        return 0

    def isadded(self):
        # None: not added
        # Download: added
        return self.download

    def on_btn_add(self):
        if self.isadded():
            remove_download(self.ihash)
            self.download = None
            self.set(self.btn_download, "Start")
            self.disable(self.btn_download)
        else:
            add_download(self.ihash, self.get(self.name))
            self.querydownload()
            self.enable(self.btn_download)
            self.set(self.btn_download, "Start")
            self.state = 1

    def on_btn_download(self):
        state = self.getstate()
        if state == 0:
            start_download(self.ihash)
            self.set(self.btn_download, "Pause")
            self.state = 1
        elif state in [1, 2]:
            stop_download(self.ihash)
            self.set(self.btn_download, "Start")
            self.state = 0

    def on_btn_close(self):
        self.close()

    def on_btn_files(self):
        files(1150, 50, "Files", self.ihash, self.info["files"])

    def on_btn_stream(self):
        pass

    def on_btn_network(self):
        check(0, 1200, "Search SWARM", self.ihash)
        self.querycache()
        self.update_ui()

    def querydownload(self):
        for download in rest.jsget("downloads", get_peers=1, get_pieces=1)[0].get("downloads", []):
            if download.get('infohash') == self.ihash:
                self.download = download
                return
        self.download = None

    def querycache(self):
        self.set(self.status, "Querying Cache...")
        self.info = rest.jsget("torrents", self.ihash, "cache")[0]
        self.set(self.status, "")

    def onloop(self):
        self.update_ui()

    def onclose(self):
        if not hash(repr(self.info)) == self.hash:
            container.refresh()


class check(gui.form):
    def init(self, ihash, refresh=1):
        self.wait = float(const.UIINTERVAL) / 5
        self.refresh = refresh
        self.ihash = ihash
        self.prg = self.progress("Progress")
        self.status = self.label("")
        self.txt = self.text("", 600)
        self.btn_recheck = self.button("Recheck", self.on_btn_recheck)
        self.btn_close = self.button("Close", self.on_btn_close)
        self._txt = ""
        self.hasrun = False

    def oninit(self):
        gui.form.oninit(self)
        self.trackers = self.querytrackers()
        self.tottime = const.TRACKERTIMEOUT * len(self.trackers)

    def on_btn_close(self):
        self.set(self.btn_close, "Closing ...")
        self.close()

    def querytrackers(self):
        return rest.jsget("torrents", self.ihash, "trackers")[0].get("trackers", [])

    def querytracker(self, tracker):
        if tracker.lower() == "dht":
            timeout = const.DHTTIMEOUT
        else:
            timeout = const.TRACKERTIMEOUT
        js, resp = rest.jsget("torrents", self.ihash, "health",
                              timeout=timeout,
                              refresh=self.refresh,
                              trackers=tracker,
                              requests={"timeout": timeout}
                              )
        if not resp:
            return True, "Timeout in %d seconds" % timeout
        status = resp.status_code
        if not status == 200:
            return True, "HTTP ERROR : %d" % status
        elif "error" in js:
            return True, js["error"]["message"]
        else:
            return False, js.get("health", {}).get(tracker, {})

    def updatetorrent(self, seeders, leechers):
        return rest.jspost("torrents", self.ihash, "health", seeders=seeders, leechers=leechers)

    def updatetext(self, txt):
        self._txt = txt + self._txt
        self.set(self.txt, self._txt)

    def on_btn_recheck(self):
        self.set(self.prg, 0)
        inittime = time.time()
        seeds = 0
        leechs = 0
        for tracker in self.trackers:
            self.set(self.status, "Tracker : %s" % tracker)
            t1 = time.time()
            err, trs = self.querytracker(tracker)
            if not err:
                se = trs.get("seeders", 0)
                le = trs.get("leechers", 0)
                seeds += se
                leechs += le
                if se + le > 0:
                    self.updatetext("------------------------------------\n")
                    self.updatetext("Tracker: %s \n" % tracker)
                    self.updatetext("    Returned %d Seeds, %d Leechs \n" % (se, le))
                    self.updatetext("    in %.1f seconds \n" % (time.time() - t1))
            t = time.time() - inittime
            self.set(self.prg, t * 100 / self.tottime)
        tottime = time.time() - inittime
        self.set(self.prg, 100)
        self.set(self.status, "Finished : S: %d, L:%d T: %.1fs" % (seeds, leechs, tottime))
        self.updatetext("++++++++++++++++++++++++++++++++++++\n")
        self.updatetext("Finished Searching: \n" +
                        "Total found %d seeders \n" % seeds +
                        "Total found %d leechers \n" % leechs +
                        "Total in %.1f seconds\n" % tottime)
        self.updatetext("++++++++++++++++++++++++++++++++++++\n")
        self.updatetorrent(seeds, leechs)

    def onloop(self):
        if not self.hasrun:
            self.on_btn_recheck()
            self.hasrun = True


class files(gui.form):
    def init(self, ihash, files=None):
        self.ihash = ihash
        if files:
            self.files = files
        else:
            self.querycache()
        for f in self.files:
            print f
            callback = self.clickfactory(self)
            bid = self.bool(f["path"], callback.onclick)
            callback.eid = bid
        self.button("Close", self.close)

    def querycache(self):
        self.files = rest.jsget("torrents", self.ihash, "cache")[0].get("files", [])

    class clickfactory():
        def __init__(self, context):
            self.gui = context

        def onclick(self):
            #  swap selection
            #self.gui.set(self.eid, not self.gui.get(self.eid))
            pass