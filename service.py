from twisted.internet import reactor

from Tribler.Core.Modules.process_checker import ProcessChecker
from Tribler.Core.Session import Session
from Tribler.Core.SessionConfig import SessionStartupConfig
import paths
import logging

from plugin import const
from plugin import log
from plugin import util

from tinyxbmc import addon

util.cleandata(const._LOGDIR)
logger = log.makelogger()


class monitor(addon.blockingloop):
    def init(self, session, wait):
        self.session = session
        self.wait = wait

    def onclose(self):
        self.session.shutdown().addCallback(reactor.stop)


class server(object):
    def __init__(self, port):
        reactor.callInThread(monitor, self.session, const.MONINTERVAL)
        logger.debug("Starting Tribler core")
        reactor.callWhenRunning(self.start, port)
        reactor.run(installSignalHandlers=0)
        logger.debug("Stopped Tribler core")

    def start(self, port):
        config = SessionStartupConfig().load()
        config.set_http_api_port(port)
        config.set_http_api_enabled(True)
        process_checker = ProcessChecker()
        if process_checker.already_running:
            logger.debug("Another Tribler Serivce is Running")
            logger.debug("Tribler can not start")
            return
        self.session = Session(config)
        self.session.start()
        # s.triblertokodi()
        logger.debug("Started Tribler core")
        for lname, logger in logging.Logger.manager.loggerDict.iteritems():
            if isinstance(logger, logging.Logger):
                log.savelogger(logger, lname)


if __name__ == '__main__':
    server(const.APIPORT)
    logger.debug("Tribler Service HIT EOF")
