import QivivoAPI
import logging


class Habitation:
    api = None
    last_presence_recorded_time = None
    events = []
    api_type: str = "habitation"
    api_sub_type: str = "data"
    settings = {'days_of_absence_before_alert': None,
                'absence_temperature': None,
                'frost_temperature': None,
                'night_temperature': None,
                'presence_temperature_1': None,
                'presence_temperature_2': None,
                'presence_temperature_3': None,
                'presence_temperature_4': None,
                'frost_protection_temperature': None}

    def __init__(self, api):
        """

        :type api: QivivoAPI.API
        """
        self.api = api
        return

    def get_last_presence(self):
        logging.info("QivivoAPI: getting last presence")
        info = self.api.get_value(self.api_type, self.api_sub_type, None, 'last-presence')
        self.last_presence_recorded_time = info['last_presence_recorded_time']
        return self.last_presence_recorded_time

    def get_events(self):
        logging.info("QivivoAPI: getting events")
        info = self.api.get_value(self.api_type, self.api_sub_type, None, 'events')
        self.events = info['events']
        return self.events

    def get_settings(self):
        logging.info("QivivoAPI: getting settings")
        info = self.api.get_value(self.api_type, self.api_sub_type, None, 'settings')
        self.settings = info['settings']
        return self.settings

    def put_setting(self,setting, value):
        self.settings[setting]=value
        payload = dict(self.settings)
        del payload['days_of_absence_before_alert']
        info = self.api.put_value(self.api_type, 'settings', None, 'define_temperature', payload)
        self.get_settings()
        return info

    def put_alert(self, value):
        payload={'new_nb_day':value}
        info = self.api.put_value(self.api_type, 'settings', None, 'define_temperature', payload)
        self.get_settings()
        return info


