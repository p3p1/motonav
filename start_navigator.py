import threading
from multiprocessing import Queue
import sys, time, datetime
from display.main_lcd import lcd_gps_data, lcd_imu1_data, lcd_imu2_data
import numpy as np
from tools.imu_parser import imu_reader
from tools.gps_parser import gps_reader
from tools.imu_init import  imu_mean_generator
__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

__timeout_queue__ = 3
_timeout_gps_restart = 6000
_timeout_gps_thread = 1
_timeout_lcd_refresh_ = 4
_timeout_save_data_ = 15

def str2float(s, decs):
    try:
        return np.around(float(s), decimals=decs)
    except ValueError:
        return float('nan')

def print_on_lcd(gps_data, imu_data):
    while True:
        _gps_packet = gps_data.get()
        _imu_packet = imu_data.get()
        print("GPS data")
        print(_gps_packet)
        print("IMU data")
        print(_imu_packet)
        print('Screen IMU1')
        lcd_imu1_data(_imu_packet)
        time.sleep(_timeout_lcd_refresh_)
        print('Screen IMU2')
        lcd_imu2_data(_imu_packet, _gps_packet)
        time.sleep(_timeout_lcd_refresh_)
        print('Screen GPS')
        lcd_gps_data(_gps_packet)
        time.sleep(_timeout_lcd_refresh_)
        del _gps_packet, _imu_packet

def save_data(filename, gps_data, imu_data):
    while True:
        _gps_packet = gps_data.get()
        _ins_packet = imu_data.get()

        _imu_values = _ins_packet[0]

        if (_imu_values[0] is None) or (_imu_values[1] is None) or (_imu_values[2] is None):
            __yaw__ = 0
            __pitch__ = 0
            __roll__ =  0
        else:
            __yaw__ = np.around(float(np.rad2deg(_imu_values[0])), decimals=2)
            __pitch__ = np.around(float(np.rad2deg(_imu_values[1])), decimals=2)
            __roll__ = np.around(float(np.rad2deg(_imu_values[2])), decimals=2)

        if (_ins_packet[1] is None) or (_ins_packet[2] is None) or (_ins_packet[3] is None):
            __baro__ = 0
            __temp__ = 0
            __alt_baro__ = 0
        else:
            __baro__ = np.around(float(_ins_packet[1]), decimals=1)
            __temp__ = np.around(float(_ins_packet[3]), decimals=1)
            __alt_baro__ = np.around(float(_ins_packet[2]), decimals=1)

        _gps_values = _gps_packet[0]
        __lat__ = str2float(_gps_values[0], 5)
        __lon__ = str2float(_gps_values[1], 5)
        __alt__ = str2float(_gps_values[2], 5)
        __mode__ = str2float(_gps_values[3], 0)
        __hdg__ = str2float(_gps_values[4], 1)
        __spd__ = str2float(_gps_values[5], 1)
        __clb__ = str2float(_gps_values[6], 1)
        __erx__ = str2float(_gps_values[7], 1)
        __ery__ = str2float(_gps_values[8], 1)
        __erz__ = str2float(_gps_values[9], 1)
        __ert__ = str2float(_gps_values[10], 1)

        __tmp_array__ = np.array([__yaw__, __pitch__, __roll__, __baro__, __temp__, __alt_baro__,
                                  __lat__, __lon__, __alt__, __mode__, __hdg__, __spd__, __clb__,
                                  __erx__, __ery__, __erz__, __ert__])
        np.savez_compressed(filename, data=__tmp_array__)
        time.sleep(_timeout_save_data_)
        del __tmp_array__, _gps_packet, _ins_packet, _imu_values
        del __yaw__, __pitch__, __roll__, __baro__, __temp__, __alt_baro__
        del __lat__, __lon__, __alt__, __mode__, __hdg__, __spd__, __clb__
        del __erx__, __ery__, __erz__, __ert__

def init_nav():
    q_stat_bias_imu = Queue()
    t_init_imu = threading.Thread(name='Init IMU', target=imu_mean_generator, args=q_stat_bias_imu)
    t_init_imu.start()
    t_init_imu.join()

def run_threads():
    q_imu = Queue()
    t_imu = threading.Thread(name='IMU Parsing', target=imu_reader, args=(q_imu, ))
    q_gps = Queue()
    t_gps = threading.Thread(name='GPS Parsing', target=gps_reader, args=(q_gps, ))
    t_print = threading.Thread(name='Print data', target=print_on_lcd, args=(q_gps, q_imu, ))

    #filename = 'log_data/' + datetime.datetime.now().strftime("%Y-%m%-%d")
    #t_save = threading.Thread(name='Save data', target=save_data, args=(filename, q_gps, q_imu, ))

    t_imu.start()
    t_print.start()
    t_gps.start()
    #t_save.start()

    t_imu.join()
    t_print.join()
    t_gps.join()
    #t_save.join()

if __name__ == '__main__':
    try:
        #init_nav()
        run_threads()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()