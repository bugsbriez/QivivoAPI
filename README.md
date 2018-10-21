# Qivivo API 2 for Python3
Python API handler for http Qivivo APi 2

## Functionality
* Create the OAuth token and keep it active
* Expose all the Qivivo web API functionality

## Installation
Require : urllib, json

## Usage
You need to create manually an application on https://account.qivivo.com/ 
and call QivivoAPI API object with the client_id and the client_secret generated.

## Exemple 
```Python
import QivivoAPI

test = QivivoAPI.API('<client_id>', '<client_secret>')
therm = None
for device in test.get_devices():
    if device['type'] == 'thermostat':
        therm = test.get_device_by_uuid(device['uuid'])

print('Temperature : ' + str(therm.get_temperature()) + '\n' +
      'Temperature Order : ' + str(therm.get_temperature_order()) + '\n' +
      'Humidity : ' + str(therm.get_humidity()) + '\n' +
      'Programs : ' + str(therm.get_programs())
      )
hab = test.get_habitation()
print('Last presence :' + str(hab.get_last_presence()) + '\n' +
      'Settings : ' + str(hab.get_settings()) + '\n' +
      'Events : ' + str(hab.get_events()))
 ```
