from threading import Thread
from tools.imu_parser import imu_reader
from tools.gps_parser import gpsReader
from router.get_directions import router


__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

threadGPS = Thread(target=gpsReader)
threadIMU = Thread(target=imu_reader(True))

threadGPS.start()
threadIMU.start()

threadGPS.join()
threadIMU.join()


