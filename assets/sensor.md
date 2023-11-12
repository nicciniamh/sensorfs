# Base class for Sensors
Every sensor in my sensor ecosystem uses this base class. A sensor has a read and write method. 
Not all sensors are readable or writeable. This is controlled by the constructor for
subclasses by passing a reader and writer method that deals with the actual job of acquiring sensor data.

This has the ability to create all sorts of sensors.
* Hardware sensors by either directly manipulating hardware or through kernel interfaces
* Virtual sensors which can do things like amalgamate other sensor data or perform calculations on one or more sensors to produce new data.
* Remote sensors where data is read from remote sources such as other devices collecting data or completely foreign sources such as *openweathermap*. 
* Something I haven't yet thought of. 

Sensors use [JSON](responsejson.html) to both read and write data. 

```python

import time 
import json
import os
import numpy as np

class Sensor:
    '''
    Class to abstract a sensor
    Requires a reader function that takes no parameters and returns a value
    Optional: a writer function that takes a data parameter and writes it to the
    sensor.
    '''

    def __init__(self,name,reader,writer=None):
        '''
        Constructor
        name: sensor name
        reader: attach function to read sensor
        writer: attach function to write sensor
        '''
        now = int(time.time())
        self.name = name
        self.ctime = self.mtime = self.atime = now
        self._reader = reader
        self.writer = writer
        self.data = None
        self.mvaLimit = 10

    def read(self):
        ''' 
        Read sensor and return data, raise IOError if not readable
        if the data dict returned contains temp, tempc, humidity or pressure
        the data is stored as a moving average of up to self.mvaLimit values using
        the _mvaData method which ensures data is within .5 to 1.5 times the moving
        average median the data is ignored but the moving average's previous value 
        is used.
        '''
        if not callable(self._reader):
            raise IOError('reader disconnected')
        self.data = self._reader()
        self.atime = int(time.time())
	self.mtime = self.atime
        self.data['name'] = self.name
        return self.data

    def write(self,data):
        ''' Write sensor with data, raise IOError if not writeable '''
        if not callable(self.writer):
            raise IOError('writer disconnected')
        self.data = data
        self.writer(data)
        self.atime = self.mtime = int(time.time())

    @property
    def isWriteable(self):
        ''' Return boolean if sensor is writeable '''
        return callable(self.writer)

    @property
    def isReadable(self):
        ''' Return boolean if sensor is readable '''
        return callable(self._reader)
```

---

<small>This page, images and code are Copyright &copy; 2023 [Nicole Stevens](/sensorfs/about.html) All rights reserved.</small>
