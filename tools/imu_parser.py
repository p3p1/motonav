import FaBo9Axis_MPU9250 as MPU9250
import time
import numpy as np
import smbus


__author__ = 'p3p1'
__copyright__ = 'Copyright 2018 p3p1'
__license__ = 'MIT'
__version__ = '0.1'

bus = smbus.SMBus(1)
#Output registers used for reference pressure: Lowest byte of reference pressure, low byte of reference pressure, high byte
#of reference pressure
ref_pressure_registers = [ 0x08, 0x09, 0x0A]
#Output registers used by the pressure sensor: Lowest byte of pressure, low byte of pressure, high byte of pressure
pressure_registers = [ 0x28, 0x29, 0x2A]
alt_compesation = 1013.25
#Output registers used by the temperature sensor: Low byte of temperature, high byte of temperature
temperature_registers = [ 0x2B, 0x2C]

def fake_imu_generator():
    _m9a = np.random.rand(3,1)
    _m9g = np.random.rand(3,1)
    _m9m = np.random.rand(3,1)
    _temp = np.random.rand(1,1)
    _press = np.random.rand(1,1)
    _alt = np.random.rand(1,1)
    return _m9a, _m9g, _m9m, _temp, _press, _alt

def return_sign_24bit(address, registers):
    """
    Return scalar representing the combined raw signed 24bit value output registers of a one-dim sensor, address is
    I2C slave address of I2C sensor, registers is list of registers
    """
    xxl = bus.read_byte_data(address,registers[0])
    xl  = bus.read_byte_data(address,registers[1])
    xh  = bus.read_byte_data(address,registers[2])

    #Combine extra low, low and high bytes to unsigned 24bit value
    x_val = (xxl | xl << 8 | xh << 16)
    if x_val < 8388608:
        pass
    else:
        x_val = x_val - 16777216

    return x_val

def return_sign_16bit(address, registers):
    """
    Return scalar representing the combined raw signed 16bit value output registers of a one-dim sensor, address is
    I2C slave address of I2C sensor, registers is list of registers
    """
    xl  = bus.read_byte_data(address,registers[0])
    xh  = bus.read_byte_data(address,registers[1])

    #Combine extra low, low and high bytes to unsigned 24bit value
    x_val = ( xl | xh << 8)
    if x_val < 32768:
        pass
    else:
        x_val = x_val - 65536

    return x_val

def imu_reader(q):
    _fake = False
    if not _fake:
        imu = MPU9250.MPU9250()
        #LPS25HB address, 0x5d, Select Control register, 0x20(32), 0x00 Power off device
        bus.write_byte_data(0x5d, 0x20, 0x00)
        time.sleep(10)
        #LPS25HB address, 0x5d, Select Control register, 0x20(32), 0x90(144) Active mode, Continous update 12.5 Hz
        bus.write_byte_data(0x5d, 0x20, 0xb0)
    else:
        print("Fake IMU data will be generated")

    time.sleep(1)

    while True:
        if not _fake:
            _accel = imu.readAccel()
            _gyro = imu.readGyro()
            _mag = imu.readMagnet()
            _accel_x = _accel['x']
            _accel_y = _accel['y']
            _accel_z = _accel['z']
            _gyro_x = _gyro['x']
            _gyro_y = _gyro['y']
            _gyro_z = _gyro['z']
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

            #print("Yaw deg", np.rad2deg(_yaw), "pitch deg", np.rad2deg(_pitch), "roll deg", np.rad2deg(_roll))
            #print("Yaw rad", _yaw, "pitch rad", _pitch, "roll deg", _roll)

            #Get the sensor data as signed 24bit value (raw)
            _curr_pressure_raw = return_sign_24bit(0x5d, pressure_registers)
            #Get the pressure in millibar = hectoPascals (hPa)
            _curr_pressure = float(_curr_pressure_raw)/4096.0
            #Get altitude in meters from US standard Atmosphere Model above level 1013.25hPa, can be adjusted to actual
            #pressure "adjusted w.r.t. to sea level" to compensate for regional and/or weather-based variations
            _curr_altitude = (1 - pow(_curr_pressure/alt_compesation, 0.190263)) * 44330.8


            #Get the sensor data as signed 16bit value (raw)
            _curr_temp_raw = return_sign_16bit(0x5d, temperature_registers)
            #Get the temperature in celsius
            _curr_temp = 42.5 + (_curr_temp_raw / 480.0)

            _ins_values = [_yaw, _pitch, _roll, _curr_altitude, _curr_pressure, _curr_temp,
                           _accel_x, _accel_y, _accel_z, _gyro_x, _gyro_y, _gyro_z,
                           _mag_x, _mag_y, _mag_y]
            q.put(_ins_values)
            time.sleep(0.01)
        else:
            _m9a, _m9g, _m9m, _temp, _press, _alt = fake_imu_generator()
            _imu_values = np.array([_m9a, _m9g, _m9m])
            _ins_values = [_imu_values, _alt, _press, _temp]

        del _ins_values


























