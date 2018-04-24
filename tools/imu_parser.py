from library.mpu9250 import MPU9250
from fake_data.generate_imu import fake_imu_generator
import time

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'


def imu_reader(fake):
    if not fake:
        imu = MPU9250()

        if imu.testConnection():
            print("Connection established with IMU: True")
        else:
            print("Connection established with IMU: False")

        imu.initialize()
    else:
        print("Fake IMU data will be generated")

    time.sleep(1)

    while True:
        if not fake:
            imu.read_all()
            imu.read_gyro()
            imu.read_acc()
            imu.read_temp()
            imu.read_mag()

            print("Accelerometer: "+str(imu.accelerometer_data))
            print("Gyroscope:     "+str(imu.gyroscope_data))
            print("Temperature:   "+str(imu.temperature))
            print("Magnetometer:  "+str(imu.magnetometer_data))

            time.sleep(0.1)
            m9a, m9g, m9m = imu.getMotion9()
        else:
            m9a, m9g, m9m = fake_imu_generator()

        print("Acc:", "{:+7.3f}".format(m9a[0]), "{:+7.3f}".format(m9a[1]), "{:+7.3f}".format(m9a[2]))
        print(" Gyr:", "{:+8.3f}".format(m9g[0]), "{:+8.3f}".format(m9g[1]), "{:+8.3f}".format(m9g[2]))
        print(" Mag:", "{:+7.3f}".format(m9m[0]), "{:+7.3f}".format(m9m[1]), "{:+7.3f}".format(m9m[2]))
        time.sleep(0.5)
