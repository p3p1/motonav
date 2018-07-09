import threading
from multiprocessing import Queue
import sys, time, datetime
from display.main_lcd import lcd_gps_data, lcd_imu1_data, lcd_imu2_data, init_nav
import numpy as np
from tools.imu_parser import imu_reader
from tools.gps_parser import gps_reader
from bluepy.btle import Scanner

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

__tout_ble__ = 60
__tout_store_data__ = .1
__tout_lcd_update__ = 10

__ble_id__ = 'd0:b5:c2:cd:3d:f2'
__ble_uuid__ = 'e2c56db5dffb48d2b060d0f5a71096e0'
__ble_pwr_tx__ = 70

def ble_scanner(q):
    __scanner__ = Scanner()
    __ble_status__ = True
    __time_found__ = time.time()
    __time_out__ = time.time()
    while True:
        __devices__ = __scanner__.scan(10.0)
        for dev in __devices__:
            print(dev.addr)
            if dev.addr == __ble_id__ and abs(dev.rssi) < abs(__ble_pwr_tx__):
                __ble_status__ = True
                __time_found__ = time.time()
                print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': BLE in range')
            else:
                print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': BLE maybe out of range')
                __time_out__ = time.time()

        if __time_out__-__time_found__ > __tout_ble__:
                __ble_status__ = False
                print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': BLE out of range')

        q.put(__ble_status__)


def str2float(s, decs):
    try:
        return np.around(float(s), decimals=decs)
    except ValueError:
        return float('nan')

def print_on_lcd(gps_data, imu_data, ble_status):
    while True:
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

def save_data(gps_data, imu_data, ble_status):
    __filename__ = '/home/pi/motonav-log/data_imu_gps-' + datetime.datetime.now().strftime("%Y_%m_%d-%H%M") + '.dat'
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start to log data in ' + __filename__ + '.')

    _ble_status = ble_status.get()
    if _ble_status:
        print('BLE in range no stop LCD')
    else:
        print('BLE out of range stop LCD')

    with open(__filename__,'ab') as f:
        while True:
            _gps_packet = gps_data.get()
            _imu_packet = imu_data.get()
            __tmp_array__ = np.empty((1,26),dtype=float)

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

def run_threads(ins_offset):
    q_imu = Queue(maxsize=1)
    q_ble = Queue(maxsize=1)
    q_gps = Queue(maxsize=1)

    t_imu = threading.Thread(name='IMU Parsing', target=imu_reader, args=(q_imu, ins_offset, ))
    t_gps = threading.Thread(name='GPS Parsing', target=gps_reader, args=(q_gps,))
    t_ble = threading.Thread(name='BLE Scanner', target=ble_scanner, args=(q_ble,))
    t_print = threading.Thread(name='Print data on LCD', target=print_on_lcd, args=(q_gps, q_imu,))
    t_save = threading.Thread(name='Save data', target=save_data, args=(q_gps, q_imu, q_ble,))

    t_imu.start()
    t_gps.start()
    t_print.start()
    t_save.start()
    t_ble.start()

    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start IMU parser thread.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start GPS parser thread.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start e-ink printer thread.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start logger data thread.')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start BLE scanner.')

    t_imu.join()
    t_gps.join()
    t_print.join()
    t_save.join()

if __name__ == '__main__':
    try:
        ins_offset = init_nav()
        run_threads(ins_offset)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()