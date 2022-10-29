#!/usr/bin/env python3
"""
This program reads 1-wire sensors from and OWFS mounted file system.
It stores the readings in an sqlite3 database
"""
import os
import sqlite3
import time

sensor_path = '/mnt/1wire/'
log_path = '~/repos/git/1-wire/log/'
dbfile = os.path.expanduser(log_path + 'temperature.db')


def connect_db(fname):
    """ Connect to a named sqlite3 database file or create one if 
        missing """
    create_tables = 0
    # A connect call creates a db file if it doesn't exist, therefore
    # we perform the file check beforehand
    if (os.path.isfile(fname) is False):
        create_tables = 1
    db = sqlite3.connect(fname)
    c = db.cursor()
    if create_tables:
        c.execute('''CREATE TABLE sensors(sensor_id text, name text,
                    timestamp text, temperature text, humidity text)''')
    return db, c


def update_db(c, device):
    """ Updates the database with a sensor reading (dict) """
    if 'humidity' not in device.keys():
        device['humidity'] = None
    if 'temperature' not in device.keys():
        device['temperature'] = None
    c.execute('''INSERT INTO sensors(sensor_id, name, timestamp,
                temperature, humidity)
                  VALUES(?,?,?,?,?)''',
                  (device['sensor_id'],
                   device['name'],
                   device['timestamp'],
                   device['temperature'],
                   device['humidity'])) 


def read_sensor(sensor):
    """ Read sensor data using information in input string[1] and
    return the sensor data[2]
    [1] '<sensor_id>:<type>:<sensor_name>'
    [2] a dict containing sensor_id, timestamp, name and value
    """
    device = {}
    sensor_id, sensor_type, name = sensor.split(':')
    fhandle = open(sensor_path + sensor_id + '/' + sensor_type, 'r')
    value = fhandle.read()
    fhandle.close()
    device['sensor_id'] = sensor_id
    device['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
    device['name'] = name
    if sensor_type == 'temperature':
        device['temperature'] = value
    if sensor_type == 'humidity':
        device['humidity'] = value
    return device


def main():
    sensor_list = ['26.B9D2BC000000:temperature:garage',
                   '26.B9D2BC000000:humidity:garage',
                   '28.B0A295040000:temperature:freezer',
                   '28.2A9FB9010000:temperature:carport']
    db, c = connect_db(dbfile)
    for sensor in sensor_list:
        device = read_sensor(sensor)
        update_db(c, device)
    db.commit()
    db.close()


if __name__ == '__main__':
    main()
