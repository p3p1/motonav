import numpy as np
import datetime
import time
import gpsd

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

max_timeout_poll = 300

def gps_init_fix():
    gpsd.connect()
    __init_status__ = False
    __lat__ = np.nan
    __lon__ = np.nan
    __start_time__ = time.time()
    while not __init_status__ and ((time.time() - __start_time__) < max_timeout_poll):
        try:
            gps_packet = gpsd.get_current()
            __lat__ = gps_packet.lat
            __lon__ = gps_packet.lon
            __init_status__ = True
            print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': First GPS fix: ' +  str(__lat__) + ' N' + str(__lon__) + ' E')
        except gpsd.NoFixError:
            __lat__ = np.nan
            __lon__ = np.nan
            __init_status__ = False
            print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': No first GPS fix.')

    _gps_status = [__lat__, __lon__, __init_status__]
    return _gps_status
