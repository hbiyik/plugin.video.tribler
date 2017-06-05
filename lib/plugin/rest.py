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


def _method(method, typ, *paths, **query):
    path = "/".join(paths)
    url = "%s://%s:%d/%s" % (const.APIPROTO,
                             const.APIDOMAIN,
                             const.APIPORT,
                             path)
    if "requests" in query:
        extra = query.pop("requests")
        kwargs = {"timeout": const.APITIMEOUT, typ: query}
        kwargs.update(extra)
    else:
        kwargs = {"timeout": const.APITIMEOUT, typ: query}
    logger.debug("Tribler REST:%s:%s:%s" % (method, url, repr(kwargs))),
    try:
        response = requests.request(method, url, **kwargs)
    except requests.exceptions.ReadTimeout:
        return {}, None
    js = response.json()
    print js
    logger.debug("Tribler REST:RESPONSE: \n %s" % pprint.pformat(js))
    return js, response


def jsget(*paths, **query):
    return _method("GET", "params", *paths, **query)


def jsput(*paths, **query):
    return _method("PUT", "json", *paths, **query)


def jspost(*paths, **query):
    return _method("POST",  "json", *paths, **query)


def jsdel(*paths, **query):
    return _method("DELETE", "json", *paths, **query)


def jspatch(*paths, **query):
    return _method("PATCH", "json", *paths, **query)
