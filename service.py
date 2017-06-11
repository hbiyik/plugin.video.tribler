from twisted.internet import reactor

from Tribler.Core.Modules.process_checker import ProcessChecker
from Tribler.Core.Session import Session
from Tribler.Core.SessionConfig import SessionStartupConfig
from Tribler.Core.simpledefs import NTFY_STARTED, NTFY_TRIBLER, STATEDIR_GUICONFIG
from Tribler.Core.Utilities.cfgparser import CallbackConfigParser
import paths
import logging
import os

from plugin import const
from plugin import log
from plugin import setting

from tinyxbmc import addon

_logger = log.getlogger()


class monitor(addon.blockingloop):
    def init(self, session, wait):
        self.session = session
        self.wait = wait

    def shut(self, *args, **kwargs):
        _logger.debug(repr(threading.enumerate()))
        _logger.debug("stopping reactor")
        reactor.stop()
        _logger.debug("reactor stopped")

    def onclose(self):
        self.session.shutdown().addCallback(self.shut)


class server(object):
    def __init__(self, port):
        config = SessionStartupConfig().load()
        config.set_http_api_port(port)
        config.set_http_api_enabled(True)
        process_checker = ProcessChecker()
        if process_checker.already_running:
            _logger.debug("Another Tribler Serivce is Running")
            _logger.debug("Tribler can not start")
            return
        self.session = Session(config)
        reactor.callInThread(monitor, self.session, const.MONINTERVAL)
        _logger.debug("Starting Tribler core")
        reactor.callWhenRunning(self.start, port)
        reactor.run(installSignalHandlers=0)
        _logger.debug("Stopped Tribler core")

    def onstart(self, subject, changetype, objectID, *args):
        gui_config_file_path = os.path.join(self.session.get_state_dir(), STATEDIR_GUICONFIG)
        tribler_gui_config = CallbackConfigParser()
        tribler_gui_config.read_file(gui_config_file_path, 'utf-8-sig')
        libtribler_settings = self.session.sessconfig.get_config_as_json()
        tribler_settings = tribler_gui_config.get_config_as_json()
        settings_dict = libtribler_settings.copy()
        settings_dict.update(tribler_settings)
        settings_dict["general"]["family_filter"] = self.session.tribler_config.config["general"]["family_filter"]
        setting.Setting.coretokodi(settings_dict)
        _logger.debug("Started Tribler core")

    def start(self, port):
        self.session.add_observer(self.onstart, NTFY_TRIBLER, [NTFY_STARTED])
        self.session.start()
        for lname, logger in logging.Logger.manager.loggerDict.iteritems():
            if isinstance(logger, logging.Logger):
                log.savelogger(logger)


if __name__ == '__main__':
    server(const.APIPORT)
    _logger.debug(repr(threading.enumerate()))
    _logger.debug("Tribler Service HIT EOF")