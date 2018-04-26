import threading
from multiprocessing import Queue
from tools.gps_parser import gps_reader
from tools.imu_parser import imu_reader
from router.router_reader import router_read_gps
import sys
from flask import Flask, Response
from flask_compress import Compress
__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

__timeout_queue__ = 30
__app__ = Flask(__name__)
__app__.config(DEBUG=False, PROPAGATE_EXCEPTIONS=True)
Compress(__app__)

def read_data(gps, imu):
    while True:
        gps_data = gps.get(__timeout_queue__)
        imu_data = imu.get(__timeout_queue__)
        print(gps_data)
        print(imu_data)

def run_jobs():
    q_gps = Queue()
    q_imu = Queue()
    t_imu = threading.Thread(name='IMU Parsing', target=imu_reader, args=(q_imu, ), daemon=True)
    t_gps = threading.Thread(name='GPS Parsing', target=gps_reader, args=(q_gps, ), daemon=True)
    t_eink = threading.Thread(name='Reader data', target=read_data, args=(q_gps, q_imu ))

    t_imu.start()
    t_gps.start()
    t_eink.start()

    t_imu.join()
    t_gps.join()
    t_eink.join()


if __name__ == '__main__':
    try:
        run_jobs()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()