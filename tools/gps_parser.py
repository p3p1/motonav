import time
from gps3 import agps3


__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

def gpsReader():
    gpsd_socket = agps3.GPSDSocket()
    gpsd_socket.connect(host='localhost', port=2947)
    gpsd_socket.watch()
    data_stream = agps3.DataStream()