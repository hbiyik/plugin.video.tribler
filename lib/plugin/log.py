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
import logging.handlers
from plugin import const
import os


class stream_proxy(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message)

    def flush(self):
        pass


def savelogger(logger, lname):
    if isinstance(logger, logging.Logger):
        lf = os.path.join(const.LOGDIR, lname + ".log")
        logfh = logging.handlers.RotatingFileHandler(lf, maxBytes=5000, encoding="utf-8")
        logfh.setLevel(const.LOGLVL)
        logfh.setFormatter(const.LOGFM)
        logger.addHandler(logfh)
        logger.setLevel(const.LOGLVL)


def makelogger():
    logger = logging.getLogger(const.ADDONNAME)
    savelogger(logger, const.ADDONNAME)
    #  sys.stderr = stream_proxy(logger, logging.DEBUG)
    #  sys.stdout = stream_proxy(logger, logging.DEBUG)
    return logger
