import time
from gps3 import agps3
import pynmea2
import numpy as np

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

filename_fake_data = 'fake_data/random_240418.nmea'
serial_name_gsp = '/dev/ttyS0'


def read_serial(serial_name):
    com = None
    reader = pynmea2.NMEAStreamReader()
    while True:
        if com is None:
            try:
                com = serial.Serial(serial_name, timeout=5.0)
            except serial.SerialException:
                print('could not connect to %s' % serial_name)
                time.sleep(5.0)
                continue

            data = com.read(16)
            for msg in reader.next(data):
                print(msg)


def gps_reader(q):
    fake = True
    if not fake:
        read_serial(serial_name_gps)
    else:
        lines = [line.rstrip('\n') for line in open(filename_fake_data)]
        i = 0
        while True:
            msg = pynmea2.parse(lines[i])
            try:
                lon = msg.longitude
                lat = msg.latitude
                data_gps = np.array([lat, lon])
                q.put(data_gps)
            except AttributeError:
                pass
            i = i + 1
            if i > len(lines)-2:
                i = 0
