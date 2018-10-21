import sys
from .qdevices import *
from .habitation import *
import urllib.request
import urllib.parse
import json


class API:
    client_id = None
    client_secret = None
    token = None
    token_date = None
    oauth_url = 'https://account.qivivo.com/oauth/token'
    api_url = 'https://data.qivivo.com/api/v2/'
    devices = []
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

    def __init__(self, clientID, clientSecret):
        # type: (str, str) -> None
        self.client_id = clientID
        self.client_secret = clientSecret
        logging.debug('QivivoAPI: object created')
        return

    def get_token(self):
        logging.debug('QivivoAPI: Asking for token')
        send_data = urllib.parse.urlencode({'grant_type': 'client_credentials',
                                            'client_id': self.client_id,
                                            'client_secret': self.client_secret,
                                            })
        send_data = send_data.encode('ascii')
        r = json.load(urllib.request.urlopen(self.oauth_url, send_data))
        self.token = r['access_token']
        self.token_date = datetime.now()
        logging.info('QivivoAPI: token initialised with: ' + self.token)

    def check_token(self):
        logging.debug('QivivoAPI: test if token is less than 30mn')
        used = datetime.now() + timedelta(minutes=30)
        if self.token_date < used:
            logging.debug('QivivoAPI: renew token')
            self.renew_token()
        else:
            logging.debug('QivivoAPI:token still OK')
            return

    def renew_token(self):
        logging.debug('QivivoAPI: Asking for token')
        send_data = urllib.parse.urlencode({'grant_type': 'client_credentials',
                                            'client_id': self.client_id,
                                            'client_secret': self.client_secret,
                                            })

        send_data = send_data.encode('ascii')
        r = json.load(urllib.request.urlopen(self.oauth_url, send_data))
        self.token = r['access_token']
        self.token_date = datetime.now()
        logging.info('QivivoAPI: token initialised with: ' + self.token)

    def get_devices(self):
        if not self.devices:
            self.refresh_devices()
        return self.devices['devices']

    def get_habitation(self):
        return Habitation(self)

    def refresh_devices(self):
        logging.info("QivivoAPI: getting devices")
        req = urllib.request.Request(self.api_url + 'devices',
                                     data=None,
                                     method='GET',
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + self.token},)
        r = json.load(urllib.request.urlopen(req))
        self.devices = r

    def get_device_by_uuid(self, uuid):
        logging.info("QivivoAPI: getting device " + uuid + " infos")
        devtype = None
        for device in self.devices['devices']:
            if device['uuid'] == uuid:
                devtype = device['type']
        logging.info("QivivoAPI: Device " + uuid + " is a " + devtype)
        if devtype == 'thermostat':
            logging.info('QivivoAPI: Adding thermostat ' + uuid)
            return Thermostat(uuid, self)
        else:
            if devtype == 'gateway':
                logging.info('QivivoAPI: Adding gateway ' + uuid)
                return Gateway(uuid, self)
            else:
                if devtype == 'wireless-module':
                    logging.info('QivivoAPI: Adding wirless module ' + uuid)
                    return WirelessModule(uuid, self)
                else:
                    logging.error('QivivoAPI: Unsupported device')
                    return None

    def get_value(self, device_type, sub_type, uuid, value):
        if uuid:
            uuid = '/' + uuid
        else:
            uuid = ''
        logging.debug(
            "QivivoAPI: getting " + value + " for " + device_type + " " + sub_type + uuid + " from " + self.api_url)
        req = urllib.request.Request(self.api_url + device_type + '/' + sub_type + uuid + '/' + value,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + self.token},
                                     method='GET')
        info = json.load(urllib.request.urlopen(req))
        return info

    def set_value(self, device_type, sub_type, uuid, value, data):
        if uuid:
            uuid = '/' + uuid
        else:
            uuid = ''
        logging.debug(
            "QivivoAPI: Setting " + value + " for " + device_type + " " + sub_type + uuid + " from " + self.api_url)
        req = urllib.request.Request(self.api_url + device_type + '/' + sub_type + '/' + uuid + '/' + value,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + self.token},
                                     method='POST',
                                     data=json.dumps(data))
        info = json.load(urllib.request.urlopen(req))
        return info

    def del_value(self, device_type, sub_type, uuid, value):
        if uuid:
            uuid = '/' + uuid
        else:
            uuid = ''
        logging.debug(
            "QivivoAPI: Deleting " + value + " for " + device_type + " " + sub_type + uuid + " from " + self.api_url)
        req = urllib.request.Request(self.api_url + device_type + '/' + sub_type + '/' + uuid + '/' + value,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + self.token},
                                     method='DELETE')
        info = json.load(urllib.request.urlopen(req))
        return info

    def put_value(self, device_type, sub_type, uuid, value, data):
        if uuid:
            uuid = '/' + uuid
        else:
            uuid = ''
        logging.debug(
            "QivivoAPI: Setting " + value + " for " + device_type + " " + sub_type + uuid + " from " + self.api_url)
        req = urllib.request.Request(self.api_url + device_type + '/' + sub_type + '/' + uuid + '/' + value,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + self.token},
                                     method='PUT',
                                     data=json.dumps(data))
        info = json.load(urllib.request.urlopen(req))
        return info
