import library.epd4in2b as epd4in2b
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import time

COLORED = 1
UNCOLORED = 0

fontmono = dict()
fontserif = dict()
fontserifbold = dict()

for i in np.arange(10, 60, 2):
    fontmono[i] = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', i)
    fontserif[i] = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', i)
    fontserifbold[i] = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', i)

def str2float(s, decs):
    try:
        return np.around(float(s), decimals=decs)
    except ValueError:
        return 'n/a'

def rotation_matrix(_x_coord, _y_coord, _x_rot_cnt, _y_rot_cnt, _rot_angle):
    if len(_x_coord) != len(_y_coord):
        print('No same length of coordinate')
        pass
    else:
        _coord_tr = np.zeros([len(_x_coord),2])
        __rot_angle_rad = np.deg2rad(_rot_angle)
        for i in np.arange(0, len(_x_coord)):
            _coord_tr[i,0] = _x_coord[i] - _x_rot_cnt
            _coord_tr[i,1] = _y_coord[i] - _y_rot_cnt
        _rot_matrix = np.array(([np.cos(__rot_angle_rad), -np.sin(__rot_angle_rad)],
                                [np.sin(__rot_angle_rad), np.cos(__rot_angle_rad)]))
        _coord_tr = np.dot(_coord_tr, _rot_matrix)
        _coord_tr_list = []
        for i in np.arange(0, len(_x_coord)):
            _coord_tr_list.append(_coord_tr[i,0] + _x_rot_cnt)
            _coord_tr_list.append(_coord_tr[i,1] + _y_rot_cnt)

        return _coord_tr_list

def lcd_imu1_data(ins_packet):
    epd = epd4in2b.EPD()
    epd.init()

    #------------------------------#
    #---- Black and red images ----#
    #------------------------------#
    _image_red_imu = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_red = ImageDraw.Draw(_image_red_imu)
    _image_black_imu = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_black = ImageDraw.Draw(_image_black_imu)

    #------------------------------#
    #--- IMU data and text boxes --#
    #------------------------------#
    _draw_black.rectangle((0, 6, 400, 36), fill=0)
    _draw_black.text((30, 10), 'IMU Data: yaw, pitch, roll', font=fontmono[24], fill=255)
    _draw_black.line((10, 240, 390, 240), fill=0)
    _draw_black.line((200, 40, 200, 240), fill=0)

    _imu_values = ins_packet[0]
    if (_imu_values[0] is None) or (_imu_values[1] is None) or (_imu_values[2] is None):
        __yaw__ = 0
        __pitch__ = 0
        __roll__ =  0
        _draw_red.text([20,260], text="N/A from IMU! Check wirings!", fill=0, font=fontserifbold[24])
    else:
        __yaw__ = np.around(float(np.rad2deg(_imu_values[0])), decimals=2)
        __pitch__ = np.around(float(np.rad2deg(_imu_values[1])), decimals=2)
        __roll__ = np.around(float(np.rad2deg(_imu_values[2])), decimals=2)
        _draw_black.text([20,260], text="Yaw: ",    fill=0, font=fontserif[22])
        _draw_black.text([150,260], text="Pitch: ", fill=0, font=fontserif[22])
        _draw_black.text([280,260], text="Roll: ",  fill=0, font=fontserif[22])
        _tmp_str_text = str(__yaw__) + u"\u00B0"
        _draw_red.text([70,260], text=_tmp_str_text,  fill=0, font=fontserifbold[22])
        _tmp_str_text = str(__pitch__)  + u"\u00B0"
        _draw_red.text([210,260], text=_tmp_str_text, fill=0, font=fontserifbold[22])
        _tmp_str_text = str(__roll__)  + u"\u00B0"
        _draw_red.text([330,260], text=_tmp_str_text, fill=0, font=fontserifbold[22])

    #------------------------------#
    #---- Artificial horizon ------#
    #------------------------------#
    _x_cent_ah = 100
    _y_cent_ah = 140
    _outer_r = 90
    _inner_r = 70

    ###--- Circles ---###
    ###Lower semi-circle, outer and inner
    _coord_circle = []
    #Calulate delta_angle for pitch angle
    _delta_angle_rad = np.arcsin(__pitch__/_inner_r)
    _delta_angle_deg = np.rad2deg(_delta_angle_rad)
    _delta_angle_deg = int(_delta_angle_deg)
    for i in np.arange(0-_delta_angle_deg,180+_delta_angle_deg):
        _x = _x_cent_ah + _inner_r*np.cos((np.deg2rad(i+__roll__)))
        _y = _y_cent_ah + _inner_r*np.sin((np.deg2rad(i+__roll__)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.polygon(_coord_circle, fill=0, outline=0)

    ##Lower semi-circle filled, outer
    _coord_circle = []
    _x = _x_cent_ah + _inner_r*np.cos((np.deg2rad(0)))
    _y = _y_cent_ah + _inner_r*np.sin((np.deg2rad(0)))
    for i in np.arange(0,181):
        _x = _x_cent_ah + _outer_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _outer_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    for i in np.arange(180,-1,-1):
        _x = _x_cent_ah + _inner_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _inner_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.polygon(_coord_circle, fill=0, outline=0)

    ##Upper semi-circle, outer
    _coord_circle = []
    for i in np.arange(180,360):
        _x = _x_cent_ah + _outer_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _outer_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.line(_coord_circle, fill=0, width=3)

    ##Lower semi-circle, inner
    _coord_circle = []
    for i in np.arange(180,360):
        _x = _x_cent_ah + _inner_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _inner_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.line(_coord_circle, fill=0, width=3)


    #Upper semi-circle, inner
    _coord_circle = []
    for i in np.arange(0,180):
        _x = _x_cent_ah + _inner_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _inner_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.line(_coord_circle, fill=255, width=3)


    ###- Indicators --###
    ##Indicator bank
    _x_ind_bank = np.array([_x_cent_ah, _x_cent_ah-5, (_x_cent_ah+5), _x_cent_ah])
    _y_ind_bank = np.array([(_y_cent_ah-_inner_r-1), (_y_cent_ah-_inner_r+15), (_y_cent_ah-_inner_r+15), (_y_cent_ah-_inner_r-1)])
    _coord_pntr_bank = rotation_matrix(_x_ind_bank, _y_ind_bank, _x_cent_ah, _y_cent_ah, -__roll__)
    _draw_red.polygon(_coord_pntr_bank, fill=0, outline=0)
    ##Notchs bank angle
    _coord_pntr_bank = [_x_cent_ah, (_y_cent_ah-_inner_r-3), _x_cent_ah-5, (_y_cent_ah-_inner_r-15), (_x_cent_ah+5), (_y_cent_ah-_inner_r-15), _x_cent_ah, (_y_cent_ah-_inner_r-3)]
    _draw_red.polygon(_coord_pntr_bank, fill=0, outline=0)

    _x_coord_pntr_bank = [_x_cent_ah, _x_cent_ah]
    _y_coord_pntr_bank = [_y_cent_ah-_inner_r-4, _y_cent_ah-_inner_r-16]
    _notch_angles = [-60, -45, -30, -20, -10, 10, 20, 30, 45, 60]

    for i in _notch_angles:
        _coord_pntr_bank = rotation_matrix(_x_coord_pntr_bank, _y_coord_pntr_bank, _x_cent_ah, _y_cent_ah, i)  #Rotation for vertical alignment
        _draw_red.line(_coord_pntr_bank, fill=0, width=4)

    ##Notchs pitch angle
    _d_x_notch_pitch = 20
    _coord_pntr_pitch = [_x_cent_ah-_d_x_notch_pitch, _y_cent_ah-2, _x_cent_ah-_d_x_notch_pitch, _y_cent_ah+2,
                         _x_cent_ah+_d_x_notch_pitch, _y_cent_ah+2, _x_cent_ah+_d_x_notch_pitch, _y_cent_ah-2 ]

    _notch_angles = np.arange(30,-40,-10)
    for i in np.arange(0, len(_notch_angles)):
        if _notch_angles[i] == 0:
            continue
        for j in np.arange(1, len(_coord_pntr_pitch), 2):
            j = int(j)
            _coord_pntr_pitch[j]=_coord_pntr_pitch[j] + _notch_angles[i]
        for j in np.arange(0, len(_coord_pntr_pitch)/2, 2):
            j = int(j)
            _coord_pntr_pitch[j]=_coord_pntr_pitch[j] - np.abs(_notch_angles[i]/2)
        for j in np.arange(len(_coord_pntr_pitch)/2, len(_coord_pntr_pitch), 2):
            j = int(j)
            _coord_pntr_pitch[j]=_coord_pntr_pitch[j] + np.abs(_notch_angles[i]/2)
        _tmp_x_pntr_pitch = np.asarray(_coord_pntr_pitch[::2])
        _tmp_y_pntr_pitch = np.asarray(_coord_pntr_pitch[1::2])
        _tmp_coord_pntr_pitch = rotation_matrix(_tmp_x_pntr_pitch, _tmp_y_pntr_pitch, _x_cent_ah, _y_cent_ah, -__roll__)
        _draw_red.polygon(_tmp_coord_pntr_pitch,fill=0, outline=255)

        for j in np.arange(1, len(_coord_pntr_pitch), 2):
            j = int(j)
            _coord_pntr_pitch[j]=_coord_pntr_pitch[j] - _notch_angles[i]
        for j in np.arange(0, len(_coord_pntr_pitch)/2, 2):
            j = int(j)
            _coord_pntr_pitch[j]=_coord_pntr_pitch[j] + np.abs(_notch_angles[i]/2)
        for j in np.arange(len(_coord_pntr_pitch)/2, len(_coord_pntr_pitch), 2):
            j = int(j)
            _coord_pntr_pitch[j]=_coord_pntr_pitch[j] - np.abs(_notch_angles[i]/2)

    ##Indicator aircraft
    _delta_x_pntr_ac = 40
    _coord_pntr_ac = [(_x_cent_ah-_delta_x_pntr_ac), (_y_cent_ah+2), (_x_cent_ah-_delta_x_pntr_ac), (_y_cent_ah+7), (_x_cent_ah-5), (_y_cent_ah+7),
                      (_x_cent_ah), (_y_cent_ah+14), (_x_cent_ah+5), (_y_cent_ah+7), (_x_cent_ah+_delta_x_pntr_ac), (_y_cent_ah+7),
                      (_x_cent_ah+_delta_x_pntr_ac), (_y_cent_ah+7), (_x_cent_ah+_delta_x_pntr_ac), (_y_cent_ah+2)]
    _draw_red.polygon(_coord_pntr_ac, fill=255, outline=0)

    ##Indicator aircraft
    _delta_x_pntr_ac = 40
    _coord_pntr_ac = [(_x_cent_ah-_delta_x_pntr_ac), (_y_cent_ah+2), (_x_cent_ah-_delta_x_pntr_ac), (_y_cent_ah+7), (_x_cent_ah-5), (_y_cent_ah+7),
                      (_x_cent_ah), (_y_cent_ah+14), (_x_cent_ah+5), (_y_cent_ah+7), (_x_cent_ah+_delta_x_pntr_ac), (_y_cent_ah+7),
                      (_x_cent_ah+_delta_x_pntr_ac), (_y_cent_ah+7), (_x_cent_ah+_delta_x_pntr_ac), (_y_cent_ah+2)]
    _draw_red.line(_coord_pntr_ac, fill=0, width=3)


    #------------------------------#
    #---------  Compass  ----------#
    #------------------------------#
    _x_cent_ah = 300
    _y_cent_ah = 140
    _outer_r = 90
    _inner_r = 70
    _black_white = 0                #If 0 white on black, if 255 black on white.
    ###--- Circles ---###
    ##Background circle
    _coord_circle = []
    for i in np.arange(0,360):
        _x = _x_cent_ah + _outer_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _outer_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _coord_circle.append(_x_cent_ah+_outer_r)
    _coord_circle.append(_y_cent_ah)
    _draw_black.polygon(_coord_circle, fill=abs(_black_white-255), outline=0)


    ###- Indicators --###
    _x_coord_pntr_hdg = [_x_cent_ah, _x_cent_ah]
    _y_coord_pntr_hdg = [_y_cent_ah-_inner_r-4, _y_cent_ah-_inner_r-16]
    _notch_angles = np.arange(0,360,15)

    for i in _notch_angles:
        _coord_pntr_hdg = rotation_matrix(_x_coord_pntr_hdg, _y_coord_pntr_hdg, _x_cent_ah, _y_cent_ah, i-180)  #Rotation for vertical alignment
        _draw_black.line(_coord_pntr_hdg, fill=abs(_black_white), width=4)

    ###- Indicators --###
    _x_coord_pntr_hdg = [_x_cent_ah, _x_cent_ah]
    _y_coord_pntr_hdg = [_y_cent_ah-_inner_r+2, _y_cent_ah-_inner_r-16]
    _notch_angles = np.arange(0,360,45)
    _delta_y_pix = 0
    _delta_x_pix = -20
    for i in _notch_angles:
        _coord_pntr_hdg = rotation_matrix(_x_coord_pntr_hdg, _y_coord_pntr_hdg, _x_cent_ah, _y_cent_ah, -i)  #Rotation for vertical alignment
        _draw_red.line(_coord_pntr_hdg, fill=0, width=6)
        _tmp_text = str(i)
        _tmp_font = fontserif[16]
        if i == 180:
            _delta_y_pix = -18
            _delta_x_pix = -4
            _tmp_font = fontserifbold[18]
            _tmp_text = "S"
        if i > 180 and i < 360:
            _delta_x_pix = 3
        if i > 0 and i < 180:
            _delta_x_pix = -22
        if i == 0:
            _delta_x_pix = -5
            _tmp_font = fontserifbold[18]
            _tmp_text = "N"
        if i == 90:
            _tmp_font = fontserifbold[18]
            _tmp_text = "E"
        if i == 270:
            _tmp_font = fontserifbold[18]
            _tmp_text = "W"

        _draw_red.text((_coord_pntr_hdg[0]+_delta_x_pix, _coord_pntr_hdg[1]+_delta_y_pix), text=_tmp_text, font=_tmp_font, fill=0)

        if i > 0 and i < 180:
            _delta_y_pix = _delta_y_pix - 6
        if i > 180 and i < 360:
            _delta_y_pix = _delta_y_pix + 7

    ##Indicator aircraft
    _x_coord_pntr_ac = np.array([_x_cent_ah-30, _x_cent_ah-30, _x_cent_ah-5, _x_cent_ah-5, _x_cent_ah, _x_cent_ah+5,
                                 _x_cent_ah+5, _x_cent_ah+30, _x_cent_ah+30, _x_cent_ah+5, _x_cent_ah+3, _x_cent_ah+10,
                                 _x_cent_ah+10, _x_cent_ah+3, _x_cent_ah, _x_cent_ah-3, _x_cent_ah-10, _x_cent_ah-10,
                                 _x_cent_ah-3, _x_cent_ah-5, _x_cent_ah-30])
    _y_coord_pntr_ac = np.array([_y_cent_ah, _y_cent_ah-5, _y_cent_ah-5, _y_cent_ah-15, _y_cent_ah-20, _y_cent_ah-15,
                                 _y_cent_ah-5, _y_cent_ah-5, _y_cent_ah+4, _y_cent_ah+8, _y_cent_ah+25, _y_cent_ah+28,
                                 _y_cent_ah+34, _y_cent_ah+36, _y_cent_ah+34, _y_cent_ah+36, _y_cent_ah+34, _y_cent_ah+28,
                                 _y_cent_ah+25, _y_cent_ah+8, _y_cent_ah+4])
    _coord_pntr_ac = rotation_matrix(_x_coord_pntr_ac, _y_coord_pntr_ac, _x_cent_ah, _y_cent_ah, -__yaw__)
    _draw_red.polygon(_coord_pntr_ac, fill=0, outline=2)

    _x_coord_pntr_ac = np.array([_x_cent_ah, _x_cent_ah-5, _x_cent_ah, _x_cent_ah+5])
    _y_coord_pntr_ac = np.array([_y_cent_ah-22, _y_cent_ah-30, _y_cent_ah-77, _y_cent_ah-30])
    _coord_pntr_ac = rotation_matrix(_x_coord_pntr_ac, _y_coord_pntr_ac, _x_cent_ah, _y_cent_ah, -__yaw__)
    _draw_red.polygon(_coord_pntr_ac, fill=0, outline=2)

    _x_coord_pntr_ac = np.array([_x_cent_ah, _x_cent_ah])
    _y_coord_pntr_ac = np.array([_y_cent_ah+40, _y_cent_ah+77])
    _coord_pntr_ac = rotation_matrix(_x_coord_pntr_ac, _y_coord_pntr_ac, _x_cent_ah, _y_cent_ah, -__yaw__)
    _draw_red.line(_coord_pntr_ac, fill=0, width=5)

    #------------------------------#
    #--- Plot results on e-ink ----#
    #------------------------------#
    epd.display_frame(epd.get_frame_buffer(_image_black_imu),epd.get_frame_buffer(_image_red_imu))

def lcd_imu2_data(ins_packet, gps_packet):
    epd = epd4in2b.EPD()
    epd.init()

    #------------------------------#
    #---- Black and red images ----#
    #------------------------------#
    _image_red_imu = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_red = ImageDraw.Draw(_image_red_imu)
    _image_black_imu = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_black = ImageDraw.Draw(_image_black_imu)

    #------------------------------#
    #--- IMU data and text boxes --#
    #------------------------------#
    _draw_black.rectangle((0, 6, 400, 36), fill=0)
    _draw_black.text((30, 10), 'IMU Data: altitude, speed', font=fontmono[24], fill=255)
    _draw_black.line((10, 240, 390, 240), fill=0)
    _draw_black.line((200, 40, 200, 240), fill=0)

    if (ins_packet[1] is None) or (ins_packet[2] is None) or (ins_packet[3] is None):
        __baro__ = 0
        _draw_red.text([10,260], text="N/A from baro!", fill=0, font=fontserifbold[24])
    else:
        __baro__ = np.around(float(ins_packet[1]), decimals=1)
        _draw_black.text([10,260], text="Height: ", fill=0, font=fontserif[24])
        _tmp_str_text = str(__baro__) + ' m'
        _draw_red.text([90,260], text=_tmp_str_text, fill=0, font=fontserifbold[24])

    _gps_data = gps_packet[0]
    if _gps_data[5] == 'n/a':
        __speed__ = 0
        _draw_red.text([190,260], text="N/A from GPS!", fill=0, font=fontserifbold[24])
    else:
        __speed__ = np.around((float(_gps_data[5])*3.6), decimals=1)
        _draw_black.text([190,260], text="Speed: ", fill=0, font=fontserif[24])
        _tmp_str_text = str(__speed__) + ' km/h'
        _draw_red.text([260,260], text=_tmp_str_text, fill=0, font=fontserifbold[24])

    #------------------------------#
    #--------  Altimeter  ---------#
    #------------------------------#
    _x_cent_ah = 100
    _y_cent_ah = 140
    _outer_r = 90
    _inner_r = 70

    _draw_black.text((_x_cent_ah-24,_y_cent_ah-70), text="Altimeter", fill=0, font=fontserif[12])
    _draw_black.text((_x_cent_ah-13,_y_cent_ah+8), text="x 10m", fill=0, font=fontserif[12])

    ###--- Circles ---###
    ##Outer circles indicator
    _coord_circle = []
    for i in np.arange(0,360):
        _x = _x_cent_ah + _outer_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _outer_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.line(_coord_circle, fill=0, width=3)

    _notch_alt_text = np.arange(0,255,5)
    _notch_alt_angles = np.linspace(30, 300, _notch_alt_text.shape[0])
    _count_line = 5
    _deltax = 0
    _deltay = 0
    for i in np.arange(0, len(_notch_alt_text)):
        _tmp_notch_speed = []
        _x = _x_cent_ah + (_inner_r+8)*np.cos((np.deg2rad(_notch_alt_angles[i]-90)))
        _y = _y_cent_ah + (_inner_r+8)*np.sin((np.deg2rad(_notch_alt_angles[i]-90)))
        _tmp_notch_speed.append(_x)
        _tmp_notch_speed.append(_y)
        _x = _x_cent_ah + (_inner_r-17)*np.cos((np.deg2rad(_notch_alt_angles[i]-90)))
        _y = _y_cent_ah + (_inner_r-17)*np.sin((np.deg2rad(_notch_alt_angles[i]-90)))
        _tmp_notch_speed.append(_x)
        _tmp_notch_speed.append(_y)
        _draw_black.line(_tmp_notch_speed, fill=0, width=2)
        if _count_line == 5:
            _count_line = 0
            _draw_black.line(_tmp_notch_speed, fill=0, width=4)
            _deltax -= 1

            if _notch_alt_text[i] >= 75  and _notch_alt_text[i] <= 100:
                _deltax += 2
                _deltay -= 4
            if _notch_alt_text[i] > 100  and _notch_alt_text[i] < 175:
                _deltax += 2
                _deltay -= 1
            if _notch_alt_text[i] == 175:
                _deltax += 8
                _deltay += 1
            if _notch_alt_text[i] > 175:
                _deltax += 6
                _deltay += 4
            if _notch_alt_text[i] == 250:
                _deltax -= 6
            _draw_black.text([_x-12+_deltax, _y-7+_deltay], text=str(_notch_alt_text[i]),  fill=0, font=fontserif[12])
        _count_line += 1

    ##Pointer altimeter
    _x_coord_pntr = np.array([_x_cent_ah, _x_cent_ah-4, _x_cent_ah, _x_cent_ah+4])
    _y_coord_pntr = np.array([_y_cent_ah, _y_cent_ah-4, _y_cent_ah - _inner_r, _y_cent_ah-4])
    _tmp_pntr_angle = np.interp(__baro__/10, _notch_alt_text, _notch_alt_angles)
    _coord_pntr = rotation_matrix(_x_coord_pntr, _y_coord_pntr, _x_cent_ah, _y_cent_ah, -_tmp_pntr_angle)
    _draw_red.polygon(_coord_pntr, fill=0, outline=255)

    #------------------------------#
    #-------  Speedometer  --------#
    #------------------------------#
    _x_cent_ah = 300
    _y_cent_ah = 140
    _outer_r = 90
    _inner_r = 70

    _draw_black.text((_x_cent_ah-14,_y_cent_ah-70), text="Speed", fill=0, font=fontserif[12])
    _draw_black.text((_x_cent_ah-10,_y_cent_ah+8), text="km/h", fill=0, font=fontserif[12])

    ###--- Circles ---###
    ##Outer circles indicator
    _coord_circle = []
    for i in np.arange(0,360):
        _x = _x_cent_ah + _outer_r*np.cos((np.deg2rad(i)))
        _y = _y_cent_ah + _outer_r*np.sin((np.deg2rad(i)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.line(_coord_circle, fill=0, width=3)

    _coord_circle = []
    for i in np.arange(180,300):
        _x = _x_cent_ah + (_inner_r+5)*np.cos((np.deg2rad(i-90)))
        _y = _y_cent_ah + (_inner_r+5)*np.sin((np.deg2rad(i-90)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    for i in np.arange(300,179,-1):
        _x = _x_cent_ah + (_outer_r-1)*np.cos((np.deg2rad(i-90)))
        _y = _y_cent_ah + (_outer_r-1)*np.sin((np.deg2rad(i-90)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_red.polygon(_coord_circle, fill=0, outline=0)

    _coord_circle = []
    for i in np.arange(30,300):
        _x = _x_cent_ah + (_inner_r+5)*np.cos((np.deg2rad(i-90)))
        _y = _y_cent_ah + (_inner_r+5)*np.sin((np.deg2rad(i-90)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    for i in np.arange(300,29,-1):
        _x = _x_cent_ah + (_inner_r-10)*np.cos((np.deg2rad(i-90)))
        _y = _y_cent_ah + (_inner_r-10)*np.sin((np.deg2rad(i-90)))
        _coord_circle.append(_x)
        _coord_circle.append(_y)
    _draw_black.polygon(_coord_circle, fill=0, outline=0)


    _notch_speed_text = np.arange(0,220,30)
    _notch_speed_angles = np.linspace(30, 300, _notch_speed_text.shape[0])
    _x_delta_text = 10
    _y_delta_text = 0
    for i in np.arange(0, len(_notch_speed_text)):
        _tmp_notch_speed = []
        _x = _x_cent_ah + (_inner_r+10)*np.cos((np.deg2rad(_notch_speed_angles[i]-90)))
        _y = _y_cent_ah + (_inner_r+10)*np.sin((np.deg2rad(_notch_speed_angles[i]-90)))
        _tmp_notch_speed.append(_x)
        _tmp_notch_speed.append(_y)
        _x = _x_cent_ah + (_inner_r-15)*np.cos((np.deg2rad(_notch_speed_angles[i]-90)))
        _y = _y_cent_ah + (_inner_r-15)*np.sin((np.deg2rad(_notch_speed_angles[i]-90)))
        _tmp_notch_speed.append(_x)
        _tmp_notch_speed.append(_y)
        if _notch_speed_text[i] <= 60:
            _x_delta_text = _x_delta_text + 4
            _y_delta_text = _y_delta_text + 2
        if _notch_speed_text[i] > 60 and _notch_speed_text[i] <= 120:
            _x_delta_text = _x_delta_text - 4
            _y_delta_text = _y_delta_text + 6
        if _notch_speed_text[i] > 120 and _notch_speed_text[i] < 180:
            _x_delta_text = _x_delta_text - 8
            _y_delta_text = _y_delta_text - 2
        if _notch_speed_text[i] >= 180:
            _x_delta_text = _x_delta_text - 10
            _y_delta_text = _y_delta_text - 6
        if _notch_speed_text[i] > 200:
            _x_delta_text = _x_delta_text + 6
        _draw_black.text((_x-_x_delta_text,_y-_y_delta_text), text=str(_notch_speed_text[i]), fill=0, font=fontserif[16])
        _draw_black.line(_tmp_notch_speed, fill=0, width=5)


    _notch_speed_text = np.arange(0,220,15)
    _notch_speed_angles = np.linspace(30, 300, _notch_speed_text.shape[0])
    for i in np.arange(0, len(_notch_speed_text)):
        _tmp_notch_speed = []
        _x = _x_cent_ah + (_inner_r+10)*np.cos((np.deg2rad(_notch_speed_angles[i]-90)))
        _y = _y_cent_ah + (_inner_r+10)*np.sin((np.deg2rad(_notch_speed_angles[i]-90)))
        _tmp_notch_speed.append(_x)
        _tmp_notch_speed.append(_y)
        _x = _x_cent_ah + (_inner_r-15)*np.cos((np.deg2rad(_notch_speed_angles[i]-90)))
        _y = _y_cent_ah + (_inner_r-15)*np.sin((np.deg2rad(_notch_speed_angles[i]-90)))
        _tmp_notch_speed.append(_x)
        _tmp_notch_speed.append(_y)
        _draw_black.line(_tmp_notch_speed, fill=0, width=2)

    ##Pointer speedometer
    _x_coord_pntr = np.array([_x_cent_ah, _x_cent_ah-4, _x_cent_ah, _x_cent_ah+4])
    _y_coord_pntr = np.array([_y_cent_ah, _y_cent_ah-4, _y_cent_ah - _inner_r, _y_cent_ah-4])
    _tmp_pntr_angle = np.interp(__speed__, _notch_speed_text, _notch_speed_angles)
    _coord_pntr = rotation_matrix(_x_coord_pntr, _y_coord_pntr, _x_cent_ah, _y_cent_ah, -_tmp_pntr_angle)
    _draw_red.polygon(_coord_pntr, fill=0, outline=255)

    epd.display_frame(epd.get_frame_buffer(_image_black_imu),epd.get_frame_buffer(_image_red_imu))

def lcd_gps_data(gps_packet):
    epd = epd4in2b.EPD()
    epd.init()

    #------------------------------#
    #---- Black and red images ----#
    #------------------------------#
    _image_red_gps = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_red = ImageDraw.Draw(_image_red_gps)
    _image_black_gps = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_black = ImageDraw.Draw(_image_black_gps)


    #------------------------------#
    #--- GPS data and text boxes --#
    #------------------------------#
    _draw_black.rectangle((0, 6, 400, 36), fill=0)
    _draw_black.text((150, 10), 'GPS Data', font=fontmono[24], fill=255)
    _draw_black.line((10, 250, 390, 250), fill=0)
    _draw_black.line((205, 40, 205, 250), fill=0)

    _mode_str = 'Mode:'
    _draw_black.text((15, 115), _mode_str, font=fontserif[18], fill=0)
    _lat_str = 'Lat: '
    _lon_str = 'Lon: '
    _alt_str = 'Alt: '
    _draw_black.text((15, 40), _lat_str, font=fontserif[24], fill=0)
    _draw_black.text((15, 65), _lon_str, font=fontserif[24], fill=0)
    _draw_black.text((15, 90), _alt_str, font=fontserif[24], fill=0)
    _spd_str = 'Speed: '
    _draw_black.text((15, 160), _spd_str, font=fontserif[24], fill=0)
    _hdg_str = 'Heading: '
    _draw_black.text((15, 190), _hdg_str, font=fontserif[24], fill=0)
    _clb_str = 'Climb: '
    _draw_black.text((15, 220), _clb_str, font= fontserif[24], fill=0)
    _erx_str = 'Lat err:'
    _draw_black.text((15, 250), _erx_str, font= fontserif[22], fill=0)
    _ery_str = 'Lon err:'
    _draw_black.text((175, 250), _ery_str, font=fontserif[22], fill=0)
    _erz_str = 'Alt err:'
    _draw_black.text((15, 275), _erz_str, font=fontserif[22], fill=0)
    _ert_str = 'Time err:'
    _draw_black.text((175, 275), _ert_str, font =fontserif[22], fill=0)
    _gps_time_str = 'Time:'
    _draw_black.text((15, 135), _gps_time_str, font=fontserif[18], fill=0)

    #_sat_list = gps_packet[1]
    _sat_list = []
    _gps_data = gps_packet[0]

    if int(_gps_data[3]) == 1:
        _nmode_str = 'No GPS fix'
        _nlat_str = 'No GPS fix!'
        _nlon_str = 'No GPS fix!'
        _nalt_str = 'No GPS fix!'
        _nhdg_str = 'n/a'
        _nspd_str = 'n/a'
        _nclb_str = 'n/a'
        _nerx_str = 'n/a'
        _nery_str = 'n/a'
        _nerz_str = 'n/a'
        _nert_str = 'n/a'
        _ngps_time_str = 'n/a'
    elif int(_gps_data[3]) == 2 or int(_gps_data[3]) == 3:
        if int(_gps_data[3]) == 2:
            _nmode_str = '2D Fix'
        elif int(_gps_data[3]) == 3:
            _nmode_str = '3D Fix'
        _ngps_time_str = gps_packet[1].strftime("%d.%m.%y %H:%M")

        _lat = str2float(_gps_data[0], 5)
        [_lat_min, _lat_deg] = np.modf(_lat)
        [_lat_sec, _lat_min] = np.modf(_lat_min*60)
        _nlat_str = str(int(_lat_deg)) + u'\u00B0' + str(int(_lat_min)) + "'" + str(np.around(_lat_sec*60, decimals=1)) + 'N'

        _lon = str2float(_gps_data[1], 5)
        [_lon_min, _lon_deg] = np.modf(_lon)
        [_lon_sec, _lon_min] = np.modf(_lon_min*60)
        _nlon_str = str(int(_lon_deg)) + u'\u00B0' + str(int(_lon_min)) + "'" + str(np.around(_lon_sec*60, decimals=1)) + 'E'

        _nalt_str = str(str2float(_gps_data[2], 5)) + ' m'
        _nhdg_str = str(str2float(_gps_data[4], 1)) + u'\u00B0'
        _nspd_str = str(str2float(_gps_data[5], 1)) + ' m/s'
        _nclb_str = str(str2float(_gps_data[6], 1)) + ' m/s'
        _nerx_str = str(str2float(_gps_data[7], 1)) + ' m'
        _nery_str = str(str2float(_gps_data[8], 1)) + ' m'
        _nerz_str = str(str2float(_gps_data[9], 1)) + ' m'
        _nert_str = str(str2float(_gps_data[10], 1)) + ' s'

    _draw_red.text((70, 40), _nlat_str, font=fontserifbold[24], fill=0)
    _draw_red.text((70, 65), _nlon_str, font=fontserifbold[24], fill=0)
    _draw_red.text((70, 90), _nalt_str, font=fontserifbold[22], fill=0)
    _draw_red.text((70, 115), _nmode_str, font=fontserifbold[18], fill=0)
    _draw_red.text((85, 160), _nspd_str, font=fontserifbold[24], fill=0)
    _draw_red.text((105, 190), _nhdg_str, font=fontserifbold[24], fill=0)
    _draw_red.text((95, 220), _nclb_str, font=fontserifbold[24], fill=0)
    _draw_red.text((95, 250), _nerx_str, font=fontserifbold[22], fill=0)
    _draw_red.text((95, 275), _nerz_str, font=fontserifbold[22], fill=0)
    _draw_red.text((265, 250), _nery_str, font=fontserifbold[22], fill=0)
    _draw_red.text((265, 275), _nert_str, font=fontserifbold[22], fill=0)
    _draw_red.text((70, 135), _ngps_time_str, font=fontserifbold[18], fill=0)


    _draw_black.line((10, 160, 205, 160), fill=0)

    #------------------------------#
    #---- Satellite Polar Chart ---#
    #------------------------------#
    _x_cent_pol = 305
    _y_cent_pol = 135
    if _mode_str == 1:
        _draw_red.text((_x_cent_pol-30, _y_cent_pol-5), font=fontserifbold[24], text="No fix!", fill=0)
    else:
        for z in np.arange(20,100,20):
            _coord_circle = []
            for i in np.arange(0,360):
                _x = _x_cent_pol + z*np.cos((np.deg2rad(i)))
                _y = _y_cent_pol + z*np.sin((np.deg2rad(i)))
                _coord_circle.append(_x)
                _coord_circle.append(_y)
            _draw_red.line(_coord_circle, fill=0, width=3)


        _radius = 80
        _coord_circle = [_x_cent_pol, _y_cent_pol]
        for i in np.arange(0,360,45):
            _x = _x_cent_pol + _radius*np.cos((np.deg2rad(i-90)))
            _y = _y_cent_pol + _radius*np.sin((np.deg2rad(i-90)))
            _coord_circle.append(_x)
            _coord_circle.append(_y)
            if (i <= 90) and (i >= 0):
                _deltay = -12
                _deltax = +3
            elif (i >= 270) and (i <= 360):
                _deltay = -12
                _deltax = -20
            else:
                _deltay = +12
                _deltax = -3
            _tmp_text = str(i)
            _draw_red.text((_x+_deltax,_y+_deltay), text=_tmp_text, fill=0)
            _draw_red.line(_coord_circle, fill=0, width=1)
            _coord_circle = [_x_cent_pol, _y_cent_pol]
        if isinstance(_sat_list, str):
            pass
        else:
            for i in np.arange(0, np.shape(_sat_list)[0]):
                if _sat_list[i,0] >= 80:
                    _radius = 79
                    _text_sat = u'\u2022'
                    _font_sat = fontserif[30]
                else:
                    _radius = _sat_list[i,0]
                    _text_sat = u'\u2726'
                    _font_sat = fontserif[24]
                _x = _x_cent_pol + _radius*np.cos(np.deg2rad(_sat_list[i,1]))
                _y = _y_cent_pol + _radius*np.sin(np.deg2rad(_sat_list[i,1]))
                _draw_red.text((_x, _y), text=_text_sat, font=_font_sat, fill=0)


    epd.display_frame(epd.get_frame_buffer(_image_black_gps),epd.get_frame_buffer(_image_red_gps))

def init_lcd(imu_init_status):
    epd = epd4in2b.EPD()
    epd.init()

    #------------------------------#
    #---- Black and red images ----#
    #------------------------------#
    _image_red_gps = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_red = ImageDraw.Draw(_image_red_gps)
    _image_black_gps = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    _draw_black = ImageDraw.Draw(_image_black_gps)

    #------------------------------#
    #---- Text and text boxes -----#
    #------------------------------#
    _draw_black.rectangle((0, 6, epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT-6), fill=0)
    _draw_black.text((30, epd4in2b.EPD_HEIGHT-40), 'Welcome back, Giuseppe!', font=fontserifbold[40], fill=255)



    ##Init IMU
    _draw_black.text((30, epd4in2b.EPD_HEIGHT+20), 'Initialization inertial... please wait!', font=fontserifbold[30], fill=255)
    epd.display_frame(epd.get_frame_buffer(_image_black_imu),epd.get_frame_buffer(_image_red_imu))


    while (imu_init == False) and (_delta_time_poll_data <= _max_timeout):
        time.sleep(1)
        _delta_time_poll_data = time.time() - _start_time_poll_data

    if _delta_time_poll_data > _max_timeout:
        _draw_black.text((230, epd4in2b.EPD_HEIGHT+20), 'IMU NOT INITIALIZED!!!', font=fontserifbold[30], fill=255)
    else:
        _draw_black.text((230, epd4in2b.EPD_HEIGHT+20), 'OK!!!', font=fontserifbold[30], fill=255)
    epd.display_frame(epd.get_frame_buffer(_image_black_imu),epd.get_frame_buffer(_image_red_imu))


    ###Init GPS
    #_draw_black.text((30, epd4in2b.EPD_HEIGHT+20), 'Initialization GPS ...', font=fontserifbold[30], fill=255)
    #epd.display_frame(epd.get_frame_buffer(_image_black_imu),epd.get_frame_buffer(_image_red_imu))

    #_max_timeout = 300

    #_start_time_poll_data = time.time()
    #time.sleep(1)
    #_delta_time_poll_data = time.time() - _start_time_poll_data

    #while (imu_init == False) and (_delta_time_poll_data <= _max_timeout):
    #    time.sleep(1)
    #    _delta_time_poll_data = time.time() - _start_time_poll_data

    #if _delta_time_poll_data > _max_timeout:
    #    _draw_black.text((230, epd4in2b.EPD_HEIGHT+20), 'NO DATA FROM GPS!!!', font=fontserifbold[30], fill=255)
    #else:
    #    _draw_black.text((230, epd4in2b.EPD_HEIGHT+20), 'OK!!!', font=fontserifbold[30], fill=255)
    #epd.display_frame(epd.get_frame_buffer(_image_black_imu),epd.get_frame_buffer(_image_red_imu))

#if __name__ == '__main__':
#    try:
#        #lcd_imu1_data()
#        lcd_imu2_data()
#        #lcd_gps_data()
#    except (KeyboardInterrupt, SystemExit):
#        sys.exit()
