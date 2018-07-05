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

def gpsd_reader(gps_daemon, q):
    while True:
        try:
            gps_packet = gps_daemon.get_current()
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

            #__sat__ = gps_packet.sats
            __tmp_gps_vars__ = np.array([__lat__, __lon__, __alt__, __mode__, __hdg__, __speed__, __climb__,
                                         __epx__, __epy__, __epv__, __ept__])

            __gps_vars__ = [__tmp_gps_vars__, gps_packet.get_time()]
            q.put(__gps_vars__)
            time.sleep(1)
            del __gps_vars__, __tmp_gps_vars__, __lat__, __lon__, __alt__, __mode__, __hdg__, __speed__, __climb__, __epx__
            del __epy__, __epv__, __ept__, gps_packet
        except gps_daemon.NoFixError:
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
            time.sleep(1)
            del __gps_vars__, __tmp_gps_vars__, __lat__, __lon__, __alt__, __mode__, __hdg__, __speed__, __climb__, __epx__
            del __epy__, __epv__, __ept__, gps_packet
            print('No GPS fix')

#def gpsd_reader(q):
#    __gps_socket__ = gps3.GPSDSocket()
#    __data_stream__ = gps3.DataStream()
#    __gps_socket__.connect(host='127.0.0.1', port=2947)
#    __gps_socket__.watch()
#    for new_data in __gps_socket__:
#        if new_data:
#            __data_stream__.unpack(new_data)
#            __alt__ = __data_stream__.TPV['alt']
#            __lat__ = __data_stream__.TPV['lat']
#            __lon__ = __data_stream__.TPV['lon']
#            __mode__ = __data_stream__.TPV['mode']
#            __hdg__ = __data_stream__.TPV['track']
#            __speed__ = __data_stream__.TPV['speed']
#            __climb__ = __data_stream__.TPV['climb']
#            __epx__ = __data_stream__.TPV['epx']
#            __epy__ = __data_stream__.TPV['epy']
#            __epv__ = __data_stream__.TPV['epv']
#            __ept__ = __data_stream__.TPV['ept']
#            __tmp_sat_list__ = __data_stream__.SKY['satellites']
#            if __tmp_sat_list__ == 'n/a':
#                __sat_list__ = __tmp_sat_list__
#            else:
#                __el_list__ = []
#                __az_list__ = []
#                for j in np.arange(0, len(__tmp_sat_list__)):
#                    if __tmp_sat_list__[j]['used']:
#                        __el_list__.append(__tmp_sat_list__[j]['el'])
#                        __az_list__.append(__tmp_sat_list__[j]['az'])
#                __sat_list__ = np.zeros([len(__az_list__),2])
#                __sat_list__[:,0] = np.asarray(__el_list__)
#                __sat_list__[:,1] = np.asarray(__az_list__)
#            __gps_vars__ = np.array([__lat__, __lon__, __alt__, __mode__, __hdg__, __speed__, __climb__,
#                                     __epx__, __epy__, __epv__, __ept__])
#            __data_gps__ = [__gps_vars__, __sat_list__]
#            q.put(__data_gps__)
#        time.sleep(40)

def gps_reader(q):
    fake = False
    if not fake:
        gpsd.connect()
        gpsd_reader(gpsd, q)
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
