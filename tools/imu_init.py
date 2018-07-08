import FaBo9Axis_MPU9250 as MPU9250
import time, datetime
import numpy as np

__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

max_timeout_poll = 3

def imu_offset_generator():
    imu = MPU9250.MPU9250()

    time.sleep(10)

    _pitch_arr = np.array([], dtype=float)
    _yaw_arr = np.array([], dtype=float)
    _roll_arr = np.array([], dtype=float)

    print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Initialization IMU started.')

    start_time = time.time()
    while (time.time()-start_time) < max_timeout_poll:
            _accel = imu.readAccel()
            _mag = imu.readMagnet()
            _accel_x = _accel['x']
            _accel_y = _accel['y']
            _accel_z = _accel['z']
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

            #print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': Initialization IMU in progress.')

    _yaw_mean = np.mean(_yaw_arr)
    _yaw_std = np.std(_yaw_arr)

    _pitch_mean = np.mean(_pitch_arr)
    _pitch_std = np.std(_pitch_arr)

    _roll_mean = np.mean(_roll_arr)
    _roll_std = np.std(_roll_arr)

    if isinstance(_yaw_mean, float) and isinstance(_pitch_mean, float) and isinstance(_roll_mean, float):
        _ins_status = [_yaw_mean, _pitch_mean, _roll_mean, _yaw_std, _pitch_std, _roll_std, True]
        print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': IMU initialized.')
        print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': IMU offset: ' + ", ".join('%5.5f'%x for x in _ins_status))
    else:
        _ins_status = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, False]
        print(datetime.datetime.now().strftime('%b-%d_%H:%M') + ': IMU initialization failed.')


    return _ins_status
























