#! /usr/bin/env python
import ow
import time
ow.init('localhost:4304')


asensor = ow.Sensor('/uncached/28.3E5A33070000').temperature

print asensor

mysensors = ow.Sensor("/uncached").sensorList( )


for sensor in mysensors :
    print sensor.address

    if sensor.address [2:14] == '3E5A33070000' :
        print sensor.temperature
