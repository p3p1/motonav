import threading
from multiprocessing import Queue
import sys, time, datetime, os
from display.main_lcd import lcd_gps_data, lcd_imu1_data, lcd_imu2_data, init_nav, goodbye
import numpy as np
from tools.imu_parser import imu_reader
from tools.gps_parser import gps_reader
import logging
__logging_filename__ = '/home/pi/motonav-log/log-' + datetime.datetime.now().strftime("%Y_%m_%d-%H%M") + '.log'
logging.basicConfig(filename=__logging_filename__,level=logging.DEBUG)

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

__tout_store_data__ = .1
__tout_lcd_update__ = 10

#__mqtt_ip__ = '127.0.0.1'
#__mqtt_port__ = 1883
#__mqtt_user__ = 'pi'
#__mqtt_pwd__ = 'fregu4e2'
__ble_file__ = '/home/pi/ble.txt'

def ble_scanner(q):
    while True:
        if os.path.exists(__ble_file__):
            q.put(True)
        else:
            q.put(False)

def str2float(s, decs):
    try:
        return np.around(float(s), decimals=decs)
    except ValueError:
        return float('nan')

def print_on_lcd(gps_data, imu_data, ble_status):
    first_out = True
    while True:
        if ble_status.get():
            first_out = True
            _gps_packet = gps_data.get()
            _imu_packet = imu_data.get()
            print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Print on e-ink firsts IMU data.')
            lcd_imu1_data(_imu_packet)
            time.sleep(__tout_lcd_update__)
            print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Print on e-ink seconds IMU data.')
            lcd_imu2_data(_imu_packet, _gps_packet)
            time.sleep(__tout_lcd_update__)
            print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Print on e-ink GPS data.')
            lcd_gps_data(_gps_packet)
            time.sleep(__tout_lcd_update__)
            del _gps_packet, _imu_packet
        else:
            if first_out:
                print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Stop print data on e-ink.')
                first_out = False
                goodbye()
            else:
                pass

def save_data(gps_data, imu_data, ble_status):
    __filename__ = '/home/pi/motonav-data/data_imu_gps-' + datetime.datetime.now().strftime("%Y_%m_%d-%H%M") + '.dat'
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start to log data in ' + __filename__ + '.')
    first_out = True
    first_start_record = True
    with open(__filename__,'ab') as f:
        while True:
            if ble_status.get():
                first_out = True
                if first_start_record:
                    print(datetime.datetime.now().strftime('%b-%d_%h:%m') + ': Recording data.')
                _gps_packet = gps_data.get()
                _imu_packet = imu_data.get()
                __tmp_array__ = np.empty((1,26),dtype=float)
                first_start_record = False
                k = 0
                for i in np.arange(0, len(_imu_packet)):
                    if _imu_packet[i] is None:
                        __tmp_array__[0,k] = np.nan
                    else:
                        __tmp_array__[0,k] = _imu_packet[i]
                    k += 1
                __tmp_gps_vars__ = _gps_packet[0]
                for i in np.arange(0, len(__tmp_gps_vars__)):
                    if __tmp_gps_vars__[i] == 'n/a':
                        __tmp_array__[0,k] = np.nan
                    else:
                        __tmp_array__[0,k] = str2float(__tmp_gps_vars__[i], 6)
                    k += 1

                np.savetxt(f,__tmp_array__,fmt='%6.6f',delimiter=',',newline='\n')
                time.sleep(__tout_store_data__)
                del _gps_packet, _imu_packet
            else:
                first_start_record = True
                if first_out:
                    print(datetime.datetime.now().strftime('%b-%d_%h:%m') + ': Stop recording data.')
                    first_out = False
                else:
                    pass

def run_threads(ins_offset):
    q_imu = Queue(maxsize=1)
    q_gps = Queue(maxsize=1)
    q_ble = Queue(maxsize=1)

    t_ble = threading.Thread(name='BLE Scanner', target=ble_scanner, args=(q_ble,))
    t_imu = threading.Thread(name='IMU Parsing', target=imu_reader, args=(q_imu, ins_offset, ))
    t_gps = threading.Thread(name='GPS Parsing', target=gps_reader, args=(q_gps,))
    t_print = threading.Thread(name='Print data on LCD', target=print_on_lcd, args=(q_gps, q_imu, q_ble,))
    t_save = threading.Thread(name='Save data', target=save_data, args=(q_gps, q_imu, q_ble,))

    t_ble.start()
    t_imu.start()
    t_gps.start()
    t_print.start()
    t_save.start()

    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start BLE scanner - File searcher.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start IMU parser thread.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start GPS parser thread.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start e-ink printer thread.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start logger data thread.')

    t_imu.join()
    t_gps.join()
    t_print.join()
    t_save.join()

if __name__ == '__main__':
    try:
        time.sleep(60)
        ins_offset = init_nav()
        run_threads(ins_offset)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()