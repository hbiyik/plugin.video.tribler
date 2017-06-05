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
from tinyxbmc import container

from plugin import rest
from plugin import torrent


class index(container.Contianer):
    def random(self):
        js = rest.jsget("torrents", "random")[0]
        for d, _ in torrent.iterate(self, js.get("torrents")):
            pass

    def play(self, ihash, name):
        torrent.download(ihash, name)
        '''
        video_port = request_variables(
            self.api_port).get('ports').get('video~port')
        Player = xbmc.Player()
        Player.play('http://localhost:%s/%s/%d' %
                    (video_port, info_hash, 0))
        '''
    def process(self, ihash):
        self.view(ihash)

    def view(self, ihash):
        torrent.ui(300, 800, "Tribler", ihash)
