#!/usr/bin/env python3

## Example HAP service for my sensors. Mostly taken from examples from HAP-Py

import os
import sys
import time
import random
import signal
import argparse

from pyhap.accessory import Accessory, Bridge
from pyhap.const import CATEGORY_SENSOR
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader

version = '0.0.1'
hostname = os.uname()[1].split('.')[0]
port = 51826

sys.path.append(os.path.expanduser('~/lib'))
from senfs import senfs

# Sensor map - set up a sensor accessory for each sensor. 
# Dictionary is keyed on host, each entry has s:sensor and n:name
sensors = {
    'piz': {'s': 'dht22', 'n': 'Living'},
    'pi3': {'s': 'si7021', 'n': 'Terry'},
    'pi4': {'s': 'aht10', 'n': 'Nikki'}
}


class senAccessory(Accessory):
    '''
    This is a class that will read sensorFS sensors using the senfs module. Sensors
    are defined by host and sensor. 
    Usage:
        senAccessory(driver,host=sensorhost,sensor=sensorname)
    '''
    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        clsargs = {}
        host = None
        sensor = None
        '''
        The accessory class doesn't like our host and sensor 
        kwargs so we grab those, and build up a new dict for 
        the kwargs for the superclass
        '''
        for k,v in kwargs.items():
            if k == 'host':
                host = v
            elif k == 'sensor':
                sensor = v
            else:
                clsargs[k] = v

        if not host or not sensor:
            raise ValueError('Host and sensor must be supplied')

        super().__init__(*args, **clsargs)

        serv_temp = self.add_preload_service('TemperatureSensor')
        serv_humidity = self.add_preload_service('HumiditySensor')

        self.char_temp = serv_temp.get_characteristic('CurrentTemperature')
        self.char_humidity = serv_humidity \
            .get_characteristic('CurrentRelativeHumidity')

        self.sensor = senfs(sensor,host,sensor,['tempc','humidity'])

    def __getstate__(self):
        state = super().__getstate__()
        state['sensor'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    @Accessory.run_at_interval(10)
    def run(self):
        try:
            data = self.sensor.read()
            self.char_temp.set_value(data['tempc'])
            self.char_humidity.set_value(data['humidity'])
        except ValueError:
            pass


def get_bridge(driver, name):
    ''' Get an accessory bridge for each defined sensor '''
    global sensors
    bridge = Bridge(driver, name)
    for host,sdef in sensors.items():
        sensor = sdef['s']
        name = sdef['n']
        sen = senAccessory(driver, name, sensor=sensor,host=host)
        bridge.add_accessory(sen)

    return bridge


if __name__ == "__main__":
    identify = f'HAP S/W Bridge v{version}'
    parser = argparse.ArgumentParser(description=identify)
    parser.add_argument('-b','--bridge',default=None,type=str,help='Set name of bridge')
    parser.add_argument('-p','--port',default=port,type=int,help='Set port of bridge')
    parser.add_argument('-v','--version',default=False, action='store_true', help='Show program version')

    args = parser.parse_args()
    if args.version:
        print(identify)
        sys.exit(1)

    if not args.bridge:
        print('No bridge specified')

    # Start the accessory on port 51826
    driver = AccessoryDriver(port=args.port,persist_file=f'~nicci/.hap/{args.bridge}.state')

    driver.add_accessory(accessory=get_bridge(driver,args.bridge))

    # We want SIGTERM (terminate) to be handled by the driver itself,
    # so that it can gracefully stop the accessory, server and advertising.
    signal.signal(signal.SIGTERM, driver.signal_handler)

    # Start it!
    driver.start()
