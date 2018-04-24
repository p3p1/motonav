import threading
import time
from tools.gps_parser import gps_reader
from tools.imu_parser import imu_reader
from router.router_reader import router_read_gps

def run_jobs():
    global lat
    global lon
    t1 = threading.Thread(name='IMU Parsing', target=imu_reader)
    t2 = threading.Thread(name='GPS Parsing', target=gps_reader)
    t1.start()
    t2.start()


if __name__ == '__main__':
    run_jobs()
