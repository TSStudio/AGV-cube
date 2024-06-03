#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import cube_recognizer.libRecognize as lR
import math

# 打开摄像头
cap = cv2.VideoCapture(0)

target_x = 320

ret, frame = cap.read()
rCN = lR.CubeRecognizer()

cur_x = target_x

end = 0
prev_x = cur_x
tgt_x = 320

try:
    while True:
        ret, frame = cap.read()
        cur_x, color, size, height = rCN.get_rec_cen(frame)
        im = frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        if (cur_x != 0 and size < 50000 and size > 1400):
            cv2.line(im, (cur_x, 0), (cur_x, 480), (0, 255, 0), 3)
            prev_x = cur_x
            cv2.putText(im, "cur_x:"+str(cur_x),
                        (10, 30), font, 1, (0, 255, 0), 2)
            if cur_x > 570:
                tgt_x = 320
            elif cur_x < 70:
                tgt_x = 320
            elif color == "green":
                tgt_x = cur_x+2.5*math.sqrt(size)
            else:
                tgt_x = cur_x-2.5*math.sqrt(size)
            if tgt_x > 560:
                tgt_x = 560
            elif tgt_x < 80:
                tgt_x = 80
            cv2.putText(im, "height:"+str(height),
                        (10, 120), font, 1, (0, 0, 255), 2)
            cv2.putText(im, "size:{:.1f}".format(size),
                        (10, 150), font, 1, (0, 0, 255), 2)
        else:
            if (prev_x < 320):
                tgt_x = 60
            else:
                tgt_x = 580
        cv2.line(im, (int(tgt_x), 0), (int(tgt_x), 480), (255, 0, 0), 3)
        cv2.putText(im, "tgt_x:"+str(tgt_x), (10, 60), font, 1, (255, 0, 0), 2)
        cv2.imshow("frame", im)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q退出
            break
except KeyboardInterrupt:
    print("End")

cap.release()
cv2.destroyAllWindows()
