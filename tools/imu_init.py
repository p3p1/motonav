import FaBo9Axis_MPU9250 as MPU9250
import time
import numpy as np

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

max_timeout_poll = 10*60

def imu_mean_generator(q):
    imu = MPU9250.MPU9250()

    time.sleep(10)

    start_time = time.time()
    time.sleep(1)

    _pitch_arr = []
    _yaw_arr = []
    _roll_arr = []

    _init_status = False
    _yaw_mean = np.nan
    _pitch_mean = np.nan
    _roll_mean = np.nan
    _yaw_std = np.nan
    _pitch_std = np.nan
    _roll_std = np.nan

    while (time.time()-start_time) < max_timeout_poll:
            _accel = imu.readAccel()
            #_gyro = imu.readGyro()
            _mag = imu.readMagnet()
            _accel_x = _accel['x']
            _accel_y = _accel['y']
            _accel_z = _accel['z']
            #_gyro_x = _gyro['x']
            #_gyro_y = _gyro['y']
            #_gyro_z = _gyro['z']
            _mag_x = _mag['x']
            _mag_y = _mag['y']
            _mag_z = _mag['z']

            #Pitch and roll calculation from acceleration along Y and X, respectively
            _pitch = np.arctan2(_accel_y, np.sqrt(_accel_x**2+_accel_z**2))
            _roll = np.arctan2(-_accel_x, np.sqrt(_accel_y**2+_accel_z**2))

            #Yaw from magnetometers, pitch and roll
            _y_yaw = (_mag_y * np.cos(_roll)) - (_mag_z*np.sin(_roll))
            _x_yaw = (_mag_x * np.cos(_pitch)) + (_mag_y*np.sin(_roll)*np.sin(_pitch)) + (_mag_z*np.cos(_roll)*np.sin(_pitch))
            _yaw = np.arctan2(_y_yaw, _x_yaw)

            _pitch_arr = np.append(_pitch_arr, _pitch)
            _roll_arr = np.append(_roll_arr, _roll)
            _yaw_arr = np.append(_yaw_arr, _yaw)

            _ins_status = [_yaw_mean, _pitch_mean, _roll_mean, _yaw_std, _pitch_std, _roll_std, _init_status]
            q.put(_ins_status)

            del _yaw, _pitch, _roll

    _yaw_mean = np.mean(_yaw_arr)
    _yaw_std = np.std(_yaw_arr)

    _pitch_mean = np.mean(_pitch_arr)
    _pitch_std = np.std(_pitch_arr)

    _roll_mean = np.mean(_roll_arr)
    _roll_std = np.std(_roll_arr)

    _init_status = True

    _ins_status = [_yaw_mean, _pitch_mean, _roll_mean, _yaw_std, _pitch_std, _roll_std, _init_status]
    q.put(_ins_status)























