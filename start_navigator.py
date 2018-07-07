import threading
from multiprocessing import Queue
import sys, time, datetime
from display.main_lcd import lcd_gps_data, lcd_imu1_data, lcd_imu2_data
import numpy as np
#import h5py
from tools.imu_parser import imu_reader
from tools.gps_parser import gps_reader
from tools.imu_init import  imu_mean_generator

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

__tout_store_data__ = .1
__tout_lcd_update__ = .1

def str2float(s, decs):
    try:
        return np.around(float(s), decimals=decs)
    except ValueError:
        return float('nan')

def print_on_lcd(gps_data, imu_data):
    while True:
        _gps_packet = gps_data.get()
        _imu_packet = imu_data.get()
        print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Print on e-ink firsts IMU data')
        lcd_imu1_data(_imu_packet)
        time.sleep(__tout_lcd_update__)
        print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Print on e-ink seconds IMU data')
        lcd_imu2_data(_imu_packet, _gps_packet)
        time.sleep(__tout_lcd_update__)
        print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Print on e-ink GPS data')
        lcd_gps_data(_gps_packet)
        time.sleep(__tout_lcd_update__)
        del _gps_packet, _imu_packet

def save_data(gps_data, imu_data):
    __filename__ = '/home/pi/motonav-log/data_imu_gps-' + datetime.datetime.now().strftime("%Y_%m_%d-%H%M") + '.dat'
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start to log data in ' + __filename__)
    #__tmp_array__ = np.zeros((26,))
    #with h5py.File(__filename__, 'a') as f:
        #dset = f.create_dataset('mydataset',data=__tmp_array__,maxshape=(None, None))
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

            #dset.resize(dset.shape[0]+__tmp_array__.shape[0],axis=0)
            #dset[__tmp_array__.shape[0]:]=__tmp_array__
            np.savetxt(f,__tmp_array__,fmt='%6.6f',delimiter=',',newline='\n')
            time.sleep(__tout_store_data__)
            del _gps_packet, _imu_packet

def init_nav():
    q_stat_bias_imu = Queue()
    t_init_imu = threading.Thread(name='Init IMU', target=imu_mean_generator, args=q_stat_bias_imu)
    t_init_imu.start()
    t_init_imu.join()

def run_threads():
    q_imu = Queue(maxsize=1)
    q_gps = Queue(maxsize=1)

    t_imu = threading.Thread(name='IMU Parsing', target=imu_reader, args=(q_imu,))
    t_gps = threading.Thread(name='GPS Parsing', target=gps_reader, args=(q_gps,))
    t_print = threading.Thread(name='Print data', target=print_on_lcd, args=(q_gps, q_imu,))
    t_save = threading.Thread(name='Save data', target=save_data, args=(q_gps, q_imu,))

    t_imu.start()
    t_gps.start()
    t_print.start()
    t_save.start()

    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start IMU parser thread')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start GPS parser thread')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start e-ink printer thread')
    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Start logger data thread')

    t_imu.join()
    t_gps.join()
    #t_print.join()
    t_save.join()

if __name__ == '__main__':
    try:
        #init_nav()
        run_threads()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()