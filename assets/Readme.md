## Code Assets

* [Base class for sensors](sensor.py)
  * [Example of Virtual Sensor combining values from two sensors and averaging common data.](aggsens.md)
  * [Example of hardware sensors accessed through Linux sysfs](i2cdev.md)
  * [Virtual CPU information sensor](cpuinfo.py)
  * [Example of I/O sensor](rgbsen.md)
* [Example response.json](responsejson.md)
* [REST API Server](restapi.py)
  * [REST API Client](httpsen.py)
* [Data base schema](schema.sql)
* [Python Collector](sencollect.py)
* [Collector Config](collect.conf)
  * [Export dictionary to /sensor/*host/sensortype/members*](senfs.md)
  * [Use sensorfs entiries as a sensor](senfs.py)
* [Check sensor health](healthcheck.py)

Tools used to collect and generate history
  * [Collect temperature history](histcollect.py)
  * [Generate history data and graphs](generate.sh)
  * [runtemphist.sh - tool to generate history data](runtemphist.sh)
  * [histread.sh - tool to generate graphs](histread.py)

