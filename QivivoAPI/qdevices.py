import logging
import QivivoAPI
from datetime import datetime, timedelta


class Device:
    """
    Parent class of Qivivo devices
    Attributes:
    uuid : str
        Unique ID of the device
    api : QivivoAPI
        API handler
    currentTimeBetweenCommunication : timedelta
        time between update between Qivivo server and physical device
    lastCommunicationDate : datetime
        date and time of the last communication between Qivivo server and physical device
    serial : str
        serial ID of the device, not used for the moment
    softwareVersion : string
        version of the device firmware, not used
    api_type : str
        first level of URI path
    device_type : str
        second level of URI path

    Methods:
    isFresh()
        check if the data need to be refreshed taking into account last communication date and the interval
    """
    uuid: str = None                                            # Unique ID of the device
    api: QivivoAPI = None                                       # API object handler
    currentTimeBetweenCommunication: timedelta = timedelta(0)   # Refresh interval of the device
    lastCommunicationDate: datetime = datetime.min              # Last update of the device on the server
    serial: str = None                                          # Serial of the device
    softwareVersion: str = None                                 # Software version of the device
    api_type: str = "devices"
    device_type: str = None                                     # Device sub type

    def __init__(self, uuid, API):
        self.uuid = uuid
        self.api = API
        return

    def isFresh(self):
        limit = self.lastCommunicationDate + self.currentTimeBetweenCommunication
        logging.debug('QivivoAPI: Refresh limit is ' + datetime.strftime(limit, "%Y-%m-%d %H:%M") +
                      ' now is ' + datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"))
        if limit < datetime.now():
            logging.debug('QivivoAPI: value not fresh')
            return False
        else:
            logging.debug('QivivoAPI: value fresh')
            return True


class Thermostat(Device):
    current_temperature_order: float = None     # Temperature order set
    temperature: float = None                   # Last reported temperature
    humidity: float = None                      # Last reported humidity
    presence_detected: bool = None              # Last reported presence
    programs = {'user_active_program_id': None,
                'user_programs': []}                               # List of programs TODO set to programs type

    def __init__(self, uuid, API):
        Device.__init__(self, uuid, API)
        self.device_type = 'thermostats'
        self.get_info(True)
        self.get_temperature(True)
        self.get_humidity(True)
        return

    def get_info(self, force=False):
        logging.debug('QivivoAPI: Getting thermostat info')
        if (not self.isFresh()) or force:
            info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'info')
            self.currentTimeBetweenCommunication = timedelta(minutes=info['currentTimeBetweenCommunication'])
            logging.debug('QivivoAPI: Setting time interval to ' + str(self.currentTimeBetweenCommunication))
            self.lastCommunicationDate = datetime.strptime(info['lastCommunicationDate'], "%Y-%m-%d %H:%M")
            logging.debug('QivivoAPI: Setting time interval to ' + str(self.lastCommunicationDate))
            self.serial = info['serial']
            self.softwareVersion = info['softwareVersion']

    def get_temperature(self, force=False):
        logging.debug('QivivoAPI: getting temperature')
        if (not self.isFresh()) or force:
            logging.debug('QivivoAPI: refreshing temperature, Force = ' + str(force))
            info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'temperature')
            self.current_temperature_order = info['current_temperature_order']
            self.temperature = info['temperature']
            self.get_info()
        return self.temperature

    def get_temperature_order(self):
        self.get_temperature()
        return self.current_temperature_order

    def get_humidity(self, force=False):
        logging.debug('QivivoAPI: getting humidity')
        if not self.isFresh() or force:
            logging.debug('QivivoAPI: refreshing humidity, Force = ' + str(force))
            info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'humidity')
            self.humidity = info['humidity']
            self.get_info()
        return self.humidity

    def get_presence(self):
        logging.debug('QivivoAPI: getting presence')
        info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'presence')
        if info['presence_detected'] == 'false':
            self.presence_detected = False
        else:
            self.presence_detected = True

    def set_temperature(self, temp, duration=120):
        logging.debug('QivivoAPI: setting temperature instruction')
        payload = {'temperature': temp,
                   'duration': duration}
        info = self.api.set_value(self.api_type, self.device_type, self.uuid, 'temperature/temporary-instruction',
                                  payload)
        return info

    def del_temperature(self):
        logging.debug('QivivoAPI: delete temperature instruction')
        info = self.api.del_value(self.api_type, self.device_type, self.uuid, 'temperature/temporary-instruction')
        return info

    def set_absence(self, start, end):
        logging.debug('QivivoAPI: set absence')
        payload = {'start_date': start,
                   'end_date': end}
        info = self.api.set_value(self.api_type, self.device_type, self.uuid, 'absence', payload)
        return info

    def del_absence(self):
        logging.debug('QivivoAPI: delete absence')
        info = self.api.del_value(self.api_type, self.device_type, self.uuid, 'absence')
        return info

    def set_arrival(self, duration):
        logging.debug('QivivoAPI: set absence')
        payload = {'duration': duration}
        info = self.api.set_value(self.api_type, self.device_type, self.uuid, 'arrival', payload)
        return info

    def del_arrival(self):
        logging.debug('QivivoAPI: delete arrival')
        info = self.api.del_value(self.api_type, self.device_type, self.uuid, 'arrival')
        return info

    def get_programs(self):
        logging.debug('QivivoAPI: getting programs')
        info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'programs')
        self.programs = info
        return self.programs

    def post_program(self,programs):
        logging.debug('QivivoAPI: posting programs')
        payload = programs
        info = self.api.post_value(self.api_type, self.device_type, self.uuid, 'programs', payload)
        self.get_programs()
        return info

    def update_program_name(self,program_id, name):
        logging.debug('QivivoAPI: Update program name')
        payload = {'new_name': name}
        info = self.api.put_value(self.api_type, self.device_type, self.uuid,
                                  'programs/' + program_id + '/name', payload)
        return info

    def update_program(self,program_id, day, periods):
        logging.debug('QivivoAPI: updating program')
        payload = {'program_day_update': periods}
        info = self.api.put_value(self.api_type, self.device_type, self.uuid,
                                  'programs/' + program_id + '/day/' + day, payload)
        return info

    def delete_program(self, program_id):
        logging.debug('QivivoAPI: Deleting program')
        info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'programs/' + program_id)
        return info


class Gateway(Device):

    def __init__(self, uuid, API):
        Device.__init__(self, uuid, API)
        logging.debug('QivivoAPI: Getting gateway info')
        self.device_type = 'gateways'
        info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'info')
        self.currentTimeBetweenCommunication = timedelta(minutes=info['currentTimeBetweenCommunication'])
        self.lastCommunicationDate = datetime.strptime(info['lastCommunicationDate'], "%Y-%m-%d %H:%M")
        self.serial = info['serial']
        self.softwareVersion = info['softwareVersion']
        return


class WirelessModule(Device):
    temperature = None
    humidity = None
    current_pilot_wire_order = None
    programs = {'user_active_program_id': None,
                'user_multizone_programs': []}

    def __init__(self, uuid, API):
        Device.__init__(self, uuid, API)
        self.device_type = 'wireless-modules'
        self.get_info()
        self.get_temperature(True)
        self.get_humidity(True)
        self.get_pilot_wire_order(True)
        if self.current_pilot_wire_order != 'monozone':
            self.get_programs()
        return

    def get_info(self):
        logging.debug('QivivoAPI: Getting gateway info')
        info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'info')
        self.currentTimeBetweenCommunication = timedelta(minutes=info['currentTimeBetweenCommunication'])
        self.lastCommunicationDate = datetime.strptime(info['lastCommunicationDate'], "%Y-%m-%d %H:%M")
        self.serial = info['serial']
        self.softwareVersion = info['softwareVersion']

    def get_temperature(self, force=False):
        logging.debug('QivivoAPI: getting temperature')
        if not self.isFresh() or force:
            logging.debug('QivivoAPI: refreshing temperature, Force = ' + str(force))
            info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'temperature')
            self.temperature = info['temperature']
            self.get_info()
        return self.temperature

    def get_humidity(self, force=False):
        logging.debug('QivivoAPI: getting humidity')
        if not self.isFresh() or force:
            logging.debug('QivivoAPI: refreshing humidity, Force = ' + str(force))
            info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'humidity')
            self.humidity = info['humidity']
            self.get_info()
        return self.humidity

    def get_pilot_wire_order(self, force=False):
        logging.debug('QivivoAPI: getting wire order')
        if not self.isFresh() or force:
            info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'pilot-wire-order')
            self.current_pilot_wire_order = info['current_pilot_wire_order']
        return self.current_pilot_wire_order

    def get_programs(self):
        logging.debug('QivivoAPI: getting programs')
        info = self.api.get_value(self.api_type, self.device_type, self.uuid, 'programs')
        self.programs = info
        return self.programs

    def put_program_active(self, program_id):
        logging.debug('QivivoAPI: Put active program')
        info = self.api.put_value(self.api_type, self.device_type, self.uuid, 'programs/' + program_id + '/active')
        return info

    def put_thermostat_zone(self):
        logging.debug('QivivoAPI: Put thermostat zone')
        info = self.api.put_value(self.api_type, self.device_type, self.uuid, 'programs/thermostat-zone')
        return info
