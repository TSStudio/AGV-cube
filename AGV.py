#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import cv2
import cube_recognizer.libRecognize as lR
from collections import OrderedDict
import math
from pid import PID
import time
# 定义引脚
EA, I2, I1, EB, I4, I3 = (13, 19, 26, 16, 20, 21)
FREQUENCY = 50

# 所有可调参数部分
##################################################################################

# PID 参数

kp = 0.39 # kp较大的情况下再对其进行调试已无意义，此时需调试下列的转向限制
ki = 0.01
kd = 0.17
target_x = 320

# 初始速度和转向限制：此阶段原作者本意为通过设置低速防止小车启动时抬头
# 实际测试时可将其作为启动前的“稳定阶段”，通过调节此阶段以适应不同的起点线距离
speed_init = 80
lim_init = 5 

stage_cutter = 10 # 从第几次循环开始阶段2：根据首个魔方与起点距离和小车初始速度调整

# 阶段2速度和转向限制
speed_st2 = 100
#30 35 38 40 45 52
lim_st2 = 47# 12 14 15 18 25

Final_Sprint = True # 是否启用阶段3直行冲刺：若末尾魔方与终点线距离较小则可关闭
# 注：进入阶段3后小车将不会接收到任何图像信号，可通过保存的movie.avi的结束时刻判断小车何时进入阶段3
sleep_time = 1 # 设置阶段3进入冲刺前的转向持续时间（秒）
# 阶段3直行冲刺速度
speed_st3 = 100

# 判定检测到的色块为有效色块的最小像素阈值：
# 若启用阶段3，该值需要仔细权衡，原因如下
# 若该值较小，则小车易将较小的杂色色块（行人衣物，魔方侧面）识别为目标，导致小车提前进入阶段3
# 若该值较大，则在魔方间距较大的情况下，小车可能会识别不到下一个魔方，在经过一个魔方之后持续反向偏转导致失败
lower_size_threshold = 800

# 小车视野中无有效色块时的转向程度(0 ~ 320)：
turn_without_target = 210


# 边沿设定（0~320）: 越小则视野范围越大，也更易检测到杂色
side_cutter = 5#75
# 与魔方目标距离系数：越大则对前方魔方更敏感，但容易提前转弯
distant_factor = 4.0 #2.7
# 目标坐标限制: 视野中存在有效色块时的转向最大程度限制，越大，转向程度的上限越小
x_lim_from_side = 90
##################################################################################

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

#循环计数器
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

last_color = "Init"
now_color = "Init"
cnt = 0
flag = 0

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
        if (cur_x != 0 and size > lower_size_threshold):
            
            now_color = color
            if now_color != last_color:
                cnt += 1
                last_color = now_color
                
            print("cnt = ",cnt)
                
            
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
                tgt_x = 320 - turn_without_target  # 60
            else:
                tgt_x = 320 + turn_without_target  # 580
            adjust = pid_line.update(tgt_x)
            if cnt >= 3 and size < 10:
                flag = 1
        cv2.line(im, (int(tgt_x), 0), (int(tgt_x), 480), (255, 0, 0), 3)
        cv2.putText(im, "tgt_x:"+str(tgt_x), (10, 60), font, 1, (255, 0, 0), 2)
        cv2.putText(im, "adj:{:.3f}".format(adjust),
                    (10, 90), font, 1, (0, 0, 255), 2)

        motor_a, motor_b = get_motor_value(adjust*lim, speed, lim)  # 计算电机速度

        pwma.ChangeDutyCycle(max(0, min(100, motor_a)))  # 设置电机速度（添加范围限制以适应高速状态）
        pwmb.ChangeDutyCycle(max(0, min(100, motor_b))) 
        
        out.write(im)
        if flag == 1:
            if Final_Sprint:
                break
            else:
                pass
    
    ##########冲线逻辑执行部分
    time.sleep(sleep_time)          
    while True:
        pwma.ChangeDutyCycle(speed_st3)   
        pwmb.ChangeDutyCycle(speed_st3)
    ##########    

except KeyboardInterrupt:
    print("End")


cap.release()
out.release()  # 关闭视频文件
cv2.destroyAllWindows()
pwma.stop()
pwmb.stop()
GPIO.cleanup()
rCN.terminate()  # IF YOU MIND THE ANONYMOUS DATA COLLECTION, COMMENT THIS LINE
