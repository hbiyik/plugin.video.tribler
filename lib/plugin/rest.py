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
import requests

from plugin import const
from plugin import log

import pprint

logger = log.makelogger()


def jsquery(*paths, **queries):
    path = "/".join(paths)
    url = "%s://%s:%d/%s" % (const.APIPROTO,
                                const.APIDOMAIN,
                                const.APIPORT,
                                path)
    logger.debug("Tribler REST:GET: %s" % url)
    response = requests.request("GET", url, timeout=const.APITIMEOUT, params=queries)
    js = response.json()
    logger.debug("Tribler REST:RESPONSE: \n %s" % pprint.pformat(js))
    return js


def jspost(*paths, **query):
    path = "/".join(paths)
    url = "%s://%s:%d/%s" % (const.APIPROTO,
                                const.APIDOMAIN,
                                const.APIPORT,
                                path)
    logger.debug("Tribler REST:PUT: %s: %s" % (url, repr(query)))
    response = requests.request("PUT", url, data=query, timeout=const.APITIMEOUT)
    js = response.json()
    logger.debug("Tribler REST:RESPONSE: \n %s" % pprint.pformat(js))
    return response, js
