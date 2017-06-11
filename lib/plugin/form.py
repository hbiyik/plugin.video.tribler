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
from tinyxbmc import gui
from tinyxbmc import addon
from tinyxbmc import container

from plugin import const
from plugin import util
from plugin import torrent
from plugin import rest

import time


class cache(gui.form):
    def init(self, ihash):
        self.wait = const.UIINTERVAL
        self.info = {}
        self.hash = None
        self.ihash = ihash
        self.state = None
        self.download = None
        self.name = self.label("Name", "")
        self.seeds = self.label(addon.local(33104).title(), "0")
        self.leechs = self.label(addon.local(33106).title(), "0")
        self.fs = self.label("Size", "")
        self.status = self.label("Status")
        self.btn_add = self.button("Add to Downloads", self.on_btn_add)
        self.btn_files = self.button("View Files", self.on_btn_files)
        self.btn_network = self.button("Query Network", self.on_btn_network)
        self.btn_close = self.button("Close", self.close)
        self.update_btns()

    def oninit(self):
        #  self.querydownload()
        gui.form.oninit(self)
        self.querycache()
        self.hash = hash(repr(self.info))
        self.update_btns()

    def update_ui(self):
        self.set(self.status, self.info["info"]["status"])
        self.set(self.name, self.info["info"]["name"])
        self.set(self.fs, util.humanbyte(self.info["info"]["size"]))
        self.set(self.seeds, str(self.info["info"]["num_seeders"]))
        self.set(self.leechs, str(self.info["info"]["num_leechers"]))
        self.set(self.status, self.info["info"]["status"])
        self.update_btns()

    def update_btns(self):
        if self.isadded():
            self.set(self.btn_add, "Remove From Downloads")
            download(300, 800, self.info["info"]["name"], self.ihash)
            self.close()
        else:
            self.set(self.btn_add, "Add To Downloads")

    def isadded(self):
        return self.info.get("info", {}).get("download", False)

    def on_btn_add(self):
        if self.isadded():
            torrent.remove_download(self.ihash)
        else:
            torrent.add_download(self.ihash, self.get(self.name))
        self.querycache()
        self.update_ui()

    def on_btn_files(self):
        files(1150, 50, "Files", self.ihash, self.info["files"])

    def on_btn_network(self):
        network(0, 1200, "Search SWARM", self.ihash)
        self.querycache()
        self.update_ui()

    def querycache(self):
        self.set(self.status, "Querying %s" % self.ihash)
        self.info = rest.jsget("torrents", self.ihash, "cache")[0]
        self.set(self.status, "")

    def onloop(self):
        self.update_ui()

    def onclose(self):
        if not hash(repr(self.info)) == self.hash:
            container.refresh()


class download(gui.form):
    def init(self, ihash):
        self.download = None
        self.ihash = ihash
        self.name = self.label("Name")
        self.prg = self.progress("Progress")
        self.filesize = self.label("Size")
        self.dspeed = self.label("Download Speed")
        self.uspeed = self.label("Upload Speed")
        self.seeders = self.label("Seeders")
        self.leechers = self.label("Leechers")
        self.hops = self.label("Hops")
        self.dprivacy = self.list("Download Privacy",
                                  ["No Privacy", "Low Privacy", "Medium Privacy", "High Privacy"])
        self.uprivacy = self.bool("Anonymous Uploading", self.on_btn_privacy)
        self.status = self.label("Status")
        self.btn_mode = self.button("Mode: Stream", self.on_btn_mode)
        self.btn_start = self.button("Start", self.on_btn_start)
        self.btn_files = self.button("Select Files", self.on_btn_files)
        self.btn_remove = self.button("Remove From Downloads", self.on_btn_remove)
        self.btn_close = self.button("Close", self.close)

    def oninit(self):
        gui.form.oninit(self)
        self.set(self.status, "Querying %s" % self.ihash)
        self.querydownload()
        self.set(self.status, "")

    def querydownlaod(self):
        self.download = rest.jsget("downloads", self.ihash)[0]["download"]

    def onloop(self):
        pass

    def update_ui(self):
        self.set(self.name, self.download["name"])
        self.set(self.progress, self.download["progress"] * 100)
        self.set(self.size, "")
        self.set(self.dspeed, "%s/s" % util.humanbyte(self.download["total_down"]))
        self.set(self.uspeed, "%s/s" % util.humanbyte(self.download["total_up"]))
        self.set(self.seeders, self.download["num_seeds"])
        self.set(self.leechers, self.download["num_peers"])
        self.set(self.hops, len(self.download["hops"]))
        self.set(self.dprivacy, self.download["anon_download"])
        self.set(self.uprivacy, bool(self.download["safe_seeding"]))
        self.set(self.status, self.download["status"])

    def on_btn_privacy(self):
        pass

    def on_btn_mode(self):
        pass

    def on_btn_start(self):
        pass

    def on_btn_remove(self):
        pass

    def on_btn_files(self):
        pass


class network(gui.form):
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