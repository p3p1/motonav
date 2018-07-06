import pynmea2
import numpy as np
#from gps3 import gps3
import time
import gpsd

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

__filename_fake_data__ = 'fake_data/random_240418.nmea'
def gps_reader(q):
    fake = False
    if not fake:
        gpsd.connect()
        while True:
            try:
                gps_packet = gpsd.get_current()
                __lat__ = gps_packet.lat
                __lon__ = gps_packet.lon
                __alt__ = gps_packet.alt
                __mode__ = gps_packet.mode
                __hdg__ = gps_packet.track
                __speed__ = gps_packet.hspeed
                __climb__ = gps_packet.climb
                try:
                    __epx__ = gps_packet.error['x']
                except KeyError:
                    __epx__ = 'n/a'
                try:
                    __epy__ = gps_packet.error['y']
                except KeyError:
                    __epy__ = 'n/a'
                try:
                    __epv__ = gps_packet.error['v']
                except KeyError:
                    __epv__ = 'n/a'
                try:
                    __ept__ = gps_packet.error['t']
                except KeyError:
                    __ept__ = 'n/a'

                __tmp_gps_vars__ = np.array([__lat__, __lon__, __alt__, __mode__, __hdg__, __speed__, __climb__,
                                             __epx__, __epy__, __epv__, __ept__])

                __gps_vars__ = [__tmp_gps_vars__, gps_packet.get_time()]
                q.put(__gps_vars__)
                time.sleep(10)
            except gpsd.NoFixError:
                __lat__ = 'n/a'
                __lon__ = 'n/a'
                __alt__ = 'n/a'
                __mode__ = 1
                __hdg__ = 'n/a'
                __speed__ = 'n/a'
                __climb__ = 'n/a'
                __epx__ = 'n/a'
                __epy__ = 'n/a'
                __epv__ = 'n/a'
                __ept__ = 'n/a'
                _gps_time__ = 'n/a'
                __tmp_gps_vars__ = np.array([__lat__, __lon__, __alt__, __mode__, __hdg__, __speed__, __climb__,
                                             __epx__, __epy__, __epv__, __ept__])

                __gps_vars__ = [__tmp_gps_vars__, _gps_time__]
                q.put(__gps_vars__)
                print('No GPS fix!')
                time.sleep(10)
            del gps_packet
    else:
        lines = [line.rstrip('\n') for line in open(__filename_fake_data__)]
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

#if __name__ == '__main__':
#    try:
#        gpsd.connect()
#        gpsd_reader(gpsd)
#    except (KeyboardInterrupt, SystemExit):
#        sys.exit()
