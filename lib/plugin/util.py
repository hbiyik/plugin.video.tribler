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
from plugin import const

import os
import shutil


def cleandata(*dirs):
    for d in dirs:
        td = os.path.join(const.DATADIR, "*")
        if os.path.exists(td):
            shutil.rmtree(td)


def humants(ts):
    # to-do: make this nested and infinite
    if not isinstance(ts, (int, float)):
        try:
            ts = int(ts)
        except ValueError:
            return '> 1 century'
    human = ""
    if ts >= 3155760000:
        human = '> 1 century'
    elif ts >= 31536000:
        human = '> 1 year'
    elif ts >= 2592000:
        human = '%dm%dd%dh%dm%ds' % (
                                     ts / 2592000,
                                     ts % 2592000 / 86400,
                                     ts % 86400 / 3600,
                                     ts % 3600 / 60,
                                     ts % 60
                                     )
    elif ts >= 86400:
        human = '%dd%dh%dm%ds' % (
                                  ts / 86400,
                                  ts % 86400 / 3600,
                                  ts % 3600 / 60,
                                  ts % 60
                                  )
    elif ts >= 3600:
        human = '%dh%dm%ds' % (
                               ts / 3600,
                               ts % 3600 / 60,
                               ts % 60
                               )
    elif ts >= 60:
        human = '%dm%ds' % (
                            ts / 60,
                            ts % 60
                            )
    elif ts > 0:
        human = '%ds' % ts % 60
    return human


def humanbyte(byte):
    # to-do: make this nested and infinite
    if not isinstance(byte, (int, float)):
        try:
            byte = int(byte)
        except ValueError:
            return 0
    if not isinstance(byte, (int, float)):
        return ""
    human = ""
    if byte < 1024:
        human = '%.1f ' % byte
    elif byte < 1024 * 1024:
        human = '%.1f K' % (byte / 1024)
    else:
        human = '%.1f M' % (byte / 1024 / 1024)
    return human
