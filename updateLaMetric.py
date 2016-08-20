#!/usr/bin/python
# encoding=utf-8

from library import lnetatmo
from library import lametric
from library import SunriseSunset
import datetime
import time
import json

# Netatmo / LaMetric Proxy
# Author : Stanislav Likavcan, likavcan@gmail.com

# A simple client which turns LaMetric into Netamo display. This client calls Netatmo API and updates LaMetric display 
# Easiest way to keep the LaMetric display updated is via cron task:
# */10 * * * * /home/lametric/updateLaMetric.py
# Don't forget to create an app within both Netatmo and LaMetric and provide your credentials here:

######################## USER SPECIFIC INFORMATION ######################

# Netatmo authentication
client_id     = '5789c1f869f740496f8b479c' 
client_secret = 'vP99i1St07uCR9B57NO44QMnjn7G9IqHOS' 
username      = 'simonegelain@gmail.com' 
password      = 'Incontro1' 

# LaMetric authentication
access_token  = 'MmYyNzA3ZGJiZGU4OTNlMTkyMDdmOWNhNDBiOWJhMzBmYjQ1N2UzNWFhMTE4NTY1MmE2NTk2NGMyNWMyNTk2YQ=='
app_id        = '4834d508cf2b0efe3157ccebcd0af004/1'

#########################################################################

# Initiate Netatmo client
authorization = lnetatmo.ClientAuth(client_id, client_secret, username, password)
devList = lnetatmo.DeviceList(authorization)
theData = devList.lastData()

# Location GPS coordinates from Netatmo
lng, lat = devList.locationData()['location']

ro = SunriseSunset.Setup(datetime.datetime.now(), latitude=lat, longitude=lng, localOffset = 1)
rise_time, set_time = ro.calculate()

for module in theData.keys():
    m_id = theData[module]['id']
    m_type = theData[module]['type']
    m_data_type = theData[module]['data_type']
    m_data = ', '.join(m_data_type)
    if (m_type == 'NAMain'):
        station_name = module
        station_id   = m_id
        print "Detected station: %s '%s' - %s, %s" % (m_id, module, m_type, m_data)
    elif (m_type == 'NAModule1' and 'CO2' not in m_data_type):
        module_name = module
        module_id   = m_id
        print "Detected module : %s '%s' - %s, %s" % (m_id, module, m_type, m_data)
    else:
        print "Detected other  : %s '%s' - %s, %s" % (m_id, module, m_type, m_data)

now   = time.time();
# Retrieve data from midnight until now
#today = time.strftime("%Y-%m-%d")
#today = int(time.mktime(time.strptime(today,"%Y-%m-%d")))
# Retrieve data for last 24hours
last_day  = now - 36 * 3600;

measure = devList.getMeasure(station_id, '1hour', 'Temperature', module_id, date_begin = last_day, date_end = now, optimize = True)

# Convert temperature values returned by Netatmo to simple field
hist_temp = [v[0] for v in measure['body'][0]['value']]

# Retrieve current sensor data
outdoor = {}
outdoor['temperature'] = str(theData[module_name]['Temperature'])+"°C"
outdoor['humidity']    = str(theData[module_name]['Humidity'])+'%'
outdoor['pressure']    = str(theData[station_name]['Pressure'])+'mb'
outdoor['trend']       = str(theData[station_name]['pressure_trend'])

print outdoor

# Icons definition
icon = {'temp': 'i2056', 'humi': 'i863', 'stable': 'i401', 'up': 'i120', 'down': 'i124', 'sunrise': 'a485', 'sunset': 'a486'}

# Post data to LaMetric
lametric = lametric.Setup()
lametric.addTextFrame(icon['temp'],outdoor['temperature'])
lametric.addSparklineFrame(hist_temp)
lametric.addTextFrame(icon['humi'],outdoor['humidity'])
lametric.addTextFrame(icon[outdoor['trend']],outdoor['pressure'])
lametric.addTextFrame(icon['sunrise'],rise_time.strftime("%H:%M"))
lametric.addTextFrame(icon['sunset'],set_time.strftime("%H:%M"))
lametric.push(app_id, access_token)
