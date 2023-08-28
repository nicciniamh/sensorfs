# Simple User Space File I/O for Sensors

## Abstract
Having a filesystem entity for sensor data fits with the Unix philosopy of "everythng is a file". This document intends to describe a system of doing this that is fairly portable across Unix-like systems. 

### Targeting the Application
Since this lays out a simple framework, it does not get into the details of the underlying hardware. Formatting the data is the responsibility of the sensor collector and the application which is using this data. 

## Sensor Filesystem
Use of small ram disks provide for non-persistent data that does not stress the devices storage. 

On Linux, I have a ramdisk on /sensor:
```
tmpfs /sensor	tmpfs nosuid,noexec,nodev,noatime,uid=1000,gid=1000,size=5M 0 0
```

This creates a 5M ramdisk with my uid/gid as owner.


## Collectors
Collectors are programs which collect sensor data from hardware and write to the sensor filesystem.

Collectors can also read files on that filesystem, use of the modification time can represent new data for example. That data can be used to control a device. 

**Collectors are not limited to hardware**
Collectors can be subscribers to MQTT brokers and write remote sensor data to the sensor filesystem.

Some sensors are not very friendly about being acccessed at the same time and timing can be an issue. In this arrangement multiple applications can read this data without disturbing the hardware. 

Consider a collector receives a message with the following json data
```
{"temp": 74.18, "tempc": 23.43, "humidity": 65.07, "time": 1693112929}
```
The collector I am running collects data in JSON format. The data then gets written to: 

```
/sensor/system/temp
/sensor/system/tempc
/sensor/system/humidity
/sensor/system/time
/sensor/system/tempdata.json
```
The temp,tempc,humidity files contain the values, time comes from the sender or sensor at the time the reading was made, tempdata.json contains the json object the other files are derived from. 

### Example
In my home I have an old Raspberry Pi 3B which has been reading the living room temperature for six years. (go little Pi!). I also have a Raspberry Pi 4b+ which is my hub to collect data.

I will, sometime soon, add an esp32 device with a sensor for yet another part of the house. 

Each of these devices publish messges with their data to a [MQTT](https://mqtt.org) broker. 

On the Pi 4, the data from these deivces is written to the /sensor filesystem. On each message the appropriate file is rewritten.
My /sensor filesystem looks like:

```
/sensor/
├── pi3
│   ├── humidity
│   ├── temp
│   ├── tempc
│   ├── tempdata.json
│   └── time
└── pi4
    ├── humidity
    ├── temp
    ├── tempc
    ├── tempdata.json
    └── time

2 directories, 10 files
```

### Sample Files

|File|Use
-----|-----------------
[collector.py](collector.py)|Example collector. I use this to collect si7021 data and export to sensorfs
[sensor.py](sensor.py)|Base class for a sensor for a consistent interface
[sensi7021.py](sensi7021.py)|Derived class from Sensor for si7021
[sensorfs.py](sensorfs.py)|Sensor filesytem utility functions (just one for now)
[fstab.snippet](fstab.snippet)|Example fstab line for a ramdisk