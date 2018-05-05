#from library.mpu9250 import MPU9250
import time
import numpy as np


__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

def fake_imu_generator():
    m9a = np.random.rand([3,1])
    m9g = np.random.rand([3,1])
    m9m = np.random.rand([3,1])
    return m9a, m9g, m9m

def imu_reader(q):
    fake = True
    if not fake:
        #imu = MPU9250()

        #if imu.testConnection():
        #    print("Connection established with IMU: True")
        #else:
        #    print("Connection established with IMU: False")

        imu.initialize()
    else:
        print("Fake IMU data will be generated")

    time.sleep(1)

    while True:
        if not fake:
            #imu.read_all()
            #imu.read_gyro()
            #imu.read_acc()
            #imu.read_temp()
            #imu.read_mag()

            #print("Accelerometer: "+str(imu.accelerometer_data))
            #print("Gyroscope:     "+str(imu.gyroscope_data))
            #print("Temperature:   "+str(imu.temperature))
            #print("Magnetometer:  "+str(imu.magnetometer_data))
            print("Test")
            #time.sleep(0.1)
            #m9a, m9g, m9m = imu.getMotion9()
        else:
            m9a, m9g, m9m = fake_imu_generator()
        #return m9a, m9g, m9m

        data_imu = np.array([m9a, m9g, m9m])
        q.put(data_imu)
