import time 
import json
import os

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
        self.reader = reader
        self.writer = writer
        self.data = None

    def read(self):
        ''' Read sensor and return data, raise IOError if not readable '''
        if not callable(self.reader):
            raise IOError('reader disconnected')
        self.data = self.reader()
        self.atime = int(time.time())
        return self.data

    def write(self,data):
        ''' Write sensor with data, raise IOError if not writeable '''
        if not callable(self.writer):
            raise IOError('writer disconnected')
        self.data = data
        self.writer(data)
        self.atime = self.mtime = int(time.time())

    def isWriteable(self):
        ''' Return boolean if sensor is writeable '''
        return callable(self.writer)

    def isReadable(self):
        ''' Return boolean if sensor is readable '''
        return callable(self.reader)