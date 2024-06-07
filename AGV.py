#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import cv2
import cube_recognizer.libRecognize as lR
from collections import OrderedDict
import math
from pid import PID

# 定义引脚
EA, I2, I1, EB, I4, I3 = (13, 19, 26, 16, 20, 21)
FREQUENCY = 50

# PID 参数
kp = 0.15
ki = 0.01
kd = 0.17
target_x = 320

# 初始速度和转向限制
speed_init = 35
lim_init = 12

stage_cutter = 30  # 从第几次循环开始阶段2

# 阶段2速度和转向限制
speed_st2 = 40  # 35 38 40 45 52
lim_st2 = 16  # 12 14 15 18 25

# 边沿设定
side_cutter = 75
# 与魔方目标距离系数
distant_factor = 2.7
# 目标坐标限制
x_lim_from_side = 90

# 设置GPIO编号模式
GPIO.setmode(GPIO.BCM)

# 设置GPIO口为输出
GPIO.setup([EA, I2, I1, EB, I4, I3], GPIO.OUT)
GPIO.output([EA, I2, EB, I3], GPIO.LOW)
GPIO.output([I1, I4], GPIO.HIGH)

# 设置PWM引脚和频率
pwma = GPIO.PWM(EA, FREQUENCY)
pwmb = GPIO.PWM(EB, FREQUENCY)
pwma.start(0)
pwmb.start(0)

# 打开摄像头
cap = cv2.VideoCapture(0)

ret, frame = cap.read()
# 循环计数器
ct = 0

cur_x = target_x
out = cv2.VideoWriter("movie.avi", cv2.VideoWriter_fourcc(
    'X', 'V', 'I', 'D'), 17, (640, 480))  # 打开/新建视频文件用于写入,帧率=17,帧尺寸=640x480


def get_motor_value(adjustment, speed, lim):  # 计算电机速度
    if abs(adjustment) > lim:
        adjustment = lim if adjustment > 0 else -lim
    return speed + adjustment, speed-adjustment


pid_line = PID(kp/100, ki/100, kd/100, target_x, 0)

print("Ready")
input()

adjust_prev = 0
adjust = 0
prev_x = cur_x
tgt_x = 320
rCN = lR.CubeRecognizer()
dict_ = OrderedDict({
    "red": 3.99,
    "orange": 20,
    "yellow": 55,
    "green": 105,
    "blue": 222})
rCN.init(140, dict_)

try:
    while True:
        if ct < stage_cutter:  # 防抬头
            speed = speed_init
            lim = lim_init
        else:
            speed = speed_st2
            lim = lim_st2
        ct = ct+1
        # 读取摄像头

        ret, frame = cap.read()

        cur_x, color, size, height = rCN.get_rec_cen(frame)

        im = frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        if (cur_x != 0 and size < 80000 and size > 1200):
            cv2.line(im, (cur_x, 0), (cur_x, 480), (0, 255, 0), 3)
            prev_x = cur_x
            cv2.putText(im, "cur_x:"+str(cur_x),
                        (10, 30), font, 1, (0, 255, 0), 2)
            if cur_x > 640-side_cutter:
                tgt_x = 320
            elif cur_x < side_cutter:
                tgt_x = 320
            elif color == "green":
                tgt_x = cur_x+distant_factor*math.sqrt(size)
            else:
                tgt_x = cur_x-distant_factor*math.sqrt(size)
            if tgt_x > 640-x_lim_from_side:
                tgt_x = 640-x_lim_from_side
            elif tgt_x < x_lim_from_side:
                tgt_x = x_lim_from_side

            cv2.putText(im, "height:"+str(height),
                        (10, 120), font, 1, (0, 0, 255), 2)
            cv2.putText(im, "size:{:.1f}".format(size),
                        (10, 150), font, 1, (0, 0, 255), 2)
            adjust = pid_line.update(tgt_x)
            adjust_prev = adjust
        elif size >= 40000:
            adjust = 0
        else:

            # adjust=pid_line.update(prev_x)
            if (prev_x < 320):
                tgt_x = 60  # 60
            else:
                tgt_x = 580  # 580
            adjust = pid_line.update(tgt_x)
        cv2.line(im, (int(tgt_x), 0), (int(tgt_x), 480), (255, 0, 0), 3)
        cv2.putText(im, "tgt_x:"+str(tgt_x), (10, 60), font, 1, (255, 0, 0), 2)
        cv2.putText(im, "adj:{:.3f}".format(adjust),
                    (10, 90), font, 1, (0, 0, 255), 2)

        motor_a, motor_b = get_motor_value(adjust*lim, speed, lim)  # 计算电机速度

        pwma.ChangeDutyCycle(motor_a)  # 设置电机速度
        pwmb.ChangeDutyCycle(motor_b)

        out.write(im)
except KeyboardInterrupt:
    print("End")


cap.release()
out.release()  # 关闭视频文件
cv2.destroyAllWindows()
pwma.stop()
pwmb.stop()
GPIO.cleanup()
rCN.terminate()  # IF YOU MIND THE ANONYMOUS DATA COLLECTION, COMMENT THIS LINE
