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
import logging
from tinyxbmc import addon
import os

ADDONNAME = "plugin.video.tribler"
APIPORT = 8085
APIDOMAIN = "localhost"
APIPROTO = "http"
PERPAGE = 9
APITIMEOUT = 5
TRACKERTIMEOUT = 3
DHTTIMEOUT = 20
LOGLVL = logging.DEBUG
LOGFM = logging.Formatter('| %(name)s | %(levelname)s | %(asctime)s | %(message)s')
MONINTERVAL = 2
UIINTERVAL = 3
CONTAINERINTERVAL = 5
DATADIR = addon.profile
_LOGDIR = "log"
LOGDIR = os.path.join(DATADIR, _LOGDIR, "")
for d in [DATADIR, LOGDIR]:
    if not os.path.exists(d):
        os.makedirs(d)
DLSTATUS = {
            'DLSTATUS_ALLOCATING_DISKSPACE': 'ALLOCATING DISKSPACE',
            'DLSTATUS_WAITING4HASHCHECK': 'WAITING FOR HASHCHECK',
            'DLSTATUS_HASHCHECKING': 'HASHCHECKING',
            'DLSTATUS_DOWNLOADING': 'DOWNLOADING',
            'DLSTATUS_SEEDING': 'SEEDING',
            'DLSTATUS_STOPPED': 'STOPPED',
            'DLSTATUS_STOPPED_ON_ERROR': 'STOPPED ON ERROR',
            'DLSTATUS_METADATA': 'FETCHING INFORMATION',
            'DLSTATUS_CIRCUITS': 'BUILDING CIRCUITS',
    }
