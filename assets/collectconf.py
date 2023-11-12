'''
Configuration for sencollect v2
'''
# these are sensorfs based sensors we collect data from
fssens = {
	'aggregate': 	'sensagg',
	'weather': 	'senweather',
	"cpu_usage": 	"cpuinfo"
}

# I2c Sensors we watch. These are created by i2cdev using the address
i2csens = {
	'aht10': 	{'address': 0x38,'name': "aht10"},
	'bmp280': 	{'address' :0x77,'name': "bmp280"},
}
print(f'Config: {fssens} {i2csens}')
