from twisted.internet import reactor

from Tribler.Core.Modules.process_checker import ProcessChecker
from Tribler.Core.Session import Session
from Tribler.Core.SessionConfig import SessionStartupConfig
import paths
import xbmc
import logging

from plugin import defs
from plugin import log
from plugin import common

common.cleandata(defs._LOGDIR)
logger = log.makelogger()


class server(object):
    def __init__(self, stopflag=False):
        self.flag = stopflag
        self.logger = logging.getLogger(defs.ADDONNAME)

    def startsession(self, port):
        config = SessionStartupConfig().load()
        config.set_http_api_port(port)
        config.set_http_api_enabled(True)
        process_checker = ProcessChecker()
        if process_checker.already_running:
            self.logger.debug("Another Tribler Serivce is Running")
            self.logger.debug("Another Tribler can not start")
            return
        self.session = Session(config)
        self.session.start()
        # s.triblertokodi()
        self.logger.debug("Started Tribler core")
        for lname, logger in logging.Logger.manager.loggerDict.iteritems():
            if isinstance(logger, logging.Logger):
                common.savelogger(logger, lname)

    def shut(self, block=2):
        try:
            mon = xbmc.Monitor()
            while not mon.abortRequested() or not self.flag:
                self.logger.debug("Entered Monitor XBMC>13")
                if mon.waitForAbort(block) or self.flag:
                    self.logger.debug("Abort Detected XBMC>13")
                    break
        except AttributeError:
            while not (xbmc.abortRequested or self.flag):
                self.logger.debug("Entered Monitor XBMC<=13")
                xbmc.sleep(block * 1000)
            self.logger.debug("Entered Monitor XBMC<=13")
        self.session.shutdown().addCallback(reactor.stop())

    def start(self, signals=0):
        reactor.callInThread(self.shut, defs.MONINTERVAL)
        self.logger.debug("Starting Tribler core")
        reactor.callWhenRunning(self.startsession, defs.APIPORT)
        reactor.run(installSignalHandlers=signals)
        self.logger.debug("Stopped Tribler core")

if __name__ == '__main__':
    core = server()
    core.start()
    logger.debug("Tribler Service HIT EOF")
