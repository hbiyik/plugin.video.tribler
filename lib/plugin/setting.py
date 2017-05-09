from plugin import rest
from tinyxbmc import addon

s = addon.setting()


class Setting(object):
    def __init__(self):
        self.koditoplugin()

    def koditoplugin(self):
        self.family_filter = s.getbool('filter.enable')
        self.exitnode = s.getbool('anony.exitnode')
        self.multichain = s.getbool('multichain.enable')
        self.download_direction = s.getstr('dllocation.path')
        self.ask_download_settings = s.getbool('dllocation.ask')
        anond = int(s.getbool('dlsetting.anond'))
        self.anond = anond + s.getint('dlsetting.anondm') * anond
        self.anonu = int(s.getbool('dlsetting.anonu') or self.anond)
        self.watch_folder = s.getbool('wfolder.enable')
        self.watch_folder_dir = s.getstr('wfolder.path')
        self.developer_mode = s.getbool('devmode.enable')
        self.port = s.getstr('firewall.port')
        self.lt_proxy_type = s.getint('tproxy.type')
        self.lt_proxy_server = s.getstr('tproxy.server')
        self.lt_proxy_port = s.getstr('tproxy.port')
        self.lt_proxy_username = s.getstr('tproxy.user')
        self.lt_proxy_password = s.getstr('tproxy.pass')
        self.bandwidth_management = s.getbool('btfeature.utp')
        self.bandwidth_connection = s.getint('btfeature.connect')
        self.upload_limit = s.getint('bwlimit.upload')
        self.download_limit = s.getint('bwlimit.download')
        self.seeding_option = s.getint('seeding.option')
        self.seeding_ratio = s.getfloat('seeding.ratio')
        self.seeding_hour = s.getint('seeding.hour')
        self.seeding_minute = s.getint('seeding.min')

    def triblertokodi(self):
        settings_data = rest.jsquery("settings").get("settings")
        seeding_modes = {
                         'forever': 0,
                         'time': 1,
                         'never': 2,
                         'ratio': 3
                         }
        s.set('filter.enable', settings_data['general']['family_filter'])
        s.set('dllocation.path', settings_data['downloadconfig']['saveas'])
        s.set('wfolder.enable', settings_data['watch_folder']['enabled'])
        s.set('wfolder.path', settings_data['watch_folder']['watch_folder_dir'])
        s.set('firewall.port', settings_data['general']['minport'])
        s.set('tproxy.type', settings_data['libtorrent']['lt_proxytype'])
        if settings_data['libtorrent']['lt_proxyserver']:
            s.set('tproxy.server', settings_data['libtorrent']['lt_proxyserver'][0])
            s.set('tproxy.port', settings_data['libtorrent']['lt_proxyserver'][1])
        else:
            s.set('tproxy.server', '')
            s.set('tproxy.port', '')
        if settings_data['libtorrent']['lt_proxyauth']:
            s.set('tproxy.user', settings_data['libtorrent']['lt_proxyauth'][0])
            s.set('tproxy.pass', settings_data['libtorrent']['lt_proxyauth'][1])
        else:
            s.set('tproxy.user', '')
            s.set('tproxy.pass', '')
        s.set('btfeature.utp', settings_data['libtorrent']['utp'])
        if settings_data['libtorrent']['max_connections_download'] == -1:
            s.set('btfeature.connect', 0)
        else:
            s.set('btfeature.connect', settings_data['libtorrent']['max_connections_download'])
        s.set('bwlimit.upload', settings_data['Tribler']['maxuploadrate'])
        s.set('bwlimit.download', settings_data['Tribler']['maxdownloadrate'])
        s.set('seeding.option', seeding_modes[settings_data['downloadconfig']['seeding_mode']])
        s.set('seeding.ratio', settings_data['downloadconfig']['seeding_ratio'])
        s.set('seeding.hour', int(settings_data['downloadconfig']['seeding_time']) / 60)
        s.set('seeding.min', int(settings_data['downloadconfig']['seeding_time']) % 60)
        s.set('anony.exitnode', settings_data['tunnel_community']['exitnode_enabled'])
        s.set('proxydl.speed', settings_data['Tribler']['default_number_hops'] - 1)
        s.set('multichain.enable', settings_data['multichain']['enabled'])

    def plugintotribler(self):
        settings_data = {
                         'general': {},
                         'Tribler': {},
                         'downloadconfig': {},
                         'libtorrent': {},
                         'watch_folder': {},
                         'tunnel_community': {},
                         'multichain': {}
                         }
        settings_data['general']['family_filter'] = self.family_filter
        settings_data['downloadconfig']['saveas'] = self.download_direction

        settings_data['watch_folder']['enabled'] = self.watch_folder
        if settings_data['watch_folder']['enabled']:
            settings_data['watch_folder']['watch_folder_dir'] = self.watch_folder_dir

        settings_data['general']['minport'] = int(self.port)
        settings_data['libtorrent']['lt_proxytype'] = self.lt_proxy_type

        if len(self.lt_proxy_server) > 0 and len(self.lt_proxy_port) > 0:
            settings_data['libtorrent']['lt_proxyserver'] = [None, None]
            settings_data['libtorrent']['lt_proxyserver'][0] = self.lt_proxy_server
            settings_data['libtorrent']['lt_proxyserver'][1] = self.lt_proxy_port

        if len(self.lt_proxy_username) > 0 and len(self.lt_proxy_password) > 0:
            settings_data['libtorrent']['lt_proxyauth'] = [None, None]
            settings_data['libtorrent']['lt_proxyauth'][0] = self.lt_proxy_username
            settings_data['libtorrent']['lt_proxyauth'][1] = self.lt_proxy_password
        settings_data['libtorrent']['utp'] = self.bandwidth_management

        if self.bandwidth_connection == 0:
            self.bandwidth_connection = -1
        settings_data['libtorrent']['max_connections_download'] = self.bandwidth_connection

        settings_data['Tribler']['maxuploadrate'] = self.upload_limit
        settings_data['Tribler']['maxdownloadrate'] = self.download_limit

        seeding_modes = ['forever', 'time', 'never', 'ratio']
        selected_mode = seeding_modes[int(self.seeding_option)]

        settings_data['downloadconfig']['seeding_mode'] = selected_mode
        settings_data['downloadconfig']['seeding_ratio'] = self.seeding_ratio

        settings_data['downloadconfig']['seeding_time'] = self.seeding_hour * \
            60 + self.seeding_minute

        settings_data['tunnel_community']['exitnode_enabled'] = self.exitnode
        settings_data['Tribler']['default_number_hops'] = self.default_hop
        settings_data['multichain']['enabled'] = self.multichain

        rest.jspost("settings", settings_data)
