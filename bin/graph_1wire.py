#!/usr/bin/env python3
"""
Reads sensor data from sqlite3 database and saves a graph using matplotlib
"""

import datetime
import matplotlib
import numpy as np
import os
import socket
import sqlite3
import time
from matplotlib import pyplot as plt, dates

sensor_path = '/mnt/1wire/'
base_dir = os.path.expanduser('~/repos/git/1-wire/')
dbfile = base_dir + 'log/temperature.db'


def connect_to_database(fname):
    """ connect to sqlite3 database with tellstick sensor readings """
    if os.path.isfile(fname) is not False:
        db = sqlite3.connect(fname)
        c = db.cursor()
        return db, c


def db_list_sensors(c):
    """ Get list of temperature and humidity sensors from database """
    sql = "SELECT DISTINCT name FROM sensors"
    c.execute(sql)
    sensor_list = c.fetchall()
    return sensor_list


def current_time():
    """ returns a string on the format 2020-06-11 14:23
        containing the current time """
    now = datetime.datetime.now()
    time_string = now.strftime('%Y-%m-%d %H:%M')
    return time_string


def date_days_ago(no_days):
    """ returns a time string with the date from <no_days> days ago
        on the format 2020-06-11 14:23 """
    now = datetime.datetime.now()
    days_ago = now - datetime.timedelta(days=no_days)
    time_string = days_ago.strftime('%Y-%m-%d %H:%M')
    return time_string


def temperature_readings(name, c, days):
    """ Function takes the following arguments:
    - name: sensor name (location)
    - c:    db cursor
    - days: time period in days
    It queries the database for all time/value pairs for that sensor going
    back the specified number of days
    """
    now = current_time()
    start_date = date_days_ago(days)
    # select timestamp, temperature from sensors where
    # name = "carport" and timestamp between
    # "2022-09-8 18:12" and "2022-09-10 18:12"
    query = (f'select timestamp, temperature from sensors where '
             f'name = "{name}" and '
             f'timestamp BETWEEN "{start_date}" and "{now}"')
    c.execute(query)
    rows = c.fetchall()
    return rows


def plot_temperature(sensor_name, c, days):
    """ Plot sensor data given the provided parameters
        sensor_name, reading, time_period """
    temp_data = temperature_readings(sensor_name, c, days)
    date_format = "%Y-%m-%d %H:%M:%S"
    y_data = np.array([float(value) for (timestamp, value) in temp_data])
    x_time = np.array([datetime.datetime.strptime(timestamp, date_format) for (timestamp, value) in temp_data])
    fig, ax = plt.subplots(1)
    plt.xlabel("Time")
    plt.ylabel("Temperature °C")
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.plot(x_time, y_data)
    plt.gcf().autofmt_xdate()
    plt.gca().set_ylim([0, None])
    if 'borken' in socket.gethostname():
        fname = f'/usr/share/nginx/www/tmp/{sensor_name}_temp.png'
    else:
        fname = f'{base_dir}graphs/{sensor_name}_temp.png'
    plt.savefig(fname, facecolor="#C2CEFF")


def main():
    db, c = connect_to_database(dbfile)
    # sensor_list = db_list_sensors(c)
    plot_temperature("carport", c, 1)
    db.close()


if __name__ == '__main__':
    main()
