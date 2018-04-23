from library.mpu9250 import MPU9250

__author__    = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__   = 'MIT'
__version__   = '0.1'

def imuReader():
    imu = MPU9250()

    if imu.testConnection():
        print("Connection established with IMU: True")
    else:
        print("Connection established with IMU: False")

    imu.initialize()

    time.sleep(1)

    while True:
        #imu.read_all()
        #imu.read_gyro()
        #imu.read_acc()
        #imu.read_temp()
        #imu.read_mag()

        #print "Accelerometer: ", imu.accelerometer_data
        #print "Gyroscope:     ", imu.gyroscope_data
        #print "Temperature:   ", imu.temperature
        #print "Magnetometer:  ", imu.magnetometer_data

        # time.sleep(0.1)

        m9a, m9g, m9m = imu.getMotion9()

        print("Acc:", "{:+7.3f}".format(m9a[0]), "{:+7.3f}".format(m9a[1]), "{:+7.3f}".format(m9a[2]))
        print(" Gyr:", "{:+8.3f}".format(m9g[0]), "{:+8.3f}".format(m9g[1]), "{:+8.3f}".format(m9g[2]))
        print(" Mag:", "{:+7.3f}".format(m9m[0]), "{:+7.3f}".format(m9m[1]), "{:+7.3f}".format(m9m[2]))

        time.sleep(0.5)