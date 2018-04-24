#from library.mpu9250 import MPU9250
from fake_data.generate_imu import fake_imu_generator
import time

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'


def imu_reader():
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
        print("Acc. x: " + str(m9a[0]) + " y: " + str(m9a[1]) + " z: " + str(m9a[2]))
        print("Gyr. x: " + str(m9g[0]) + " y: " + str(m9g[1]) + " z: " + str(m9g[2]))
        print("Mag. x: " + str(m9m[0]) + " y: " + str(m9m[1]) + " z: " + str(m9m[2]))
        #time.sleep(0.5)

