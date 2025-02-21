from collections import OrderedDict
import numpy as np
import imutils
import cv2
from time import time
from urllib.parse import quote, unquote

class ColorLabeler:
    def __init__(self,dict_=None):
        if dict_ is None:
            dict_ = OrderedDict({
                "red": 3.99,
                "orange": 20,
                "yellow": 55,
                "green": 105,
                "blue": 222})
        colors = dict_
        self.vectors = []
        self.colorNames = []
        for (i, (name, degree)) in enumerate(colors.items()):
            self.colorNames.append(name)
            self.vectors.append(
                [np.cos(np.radians(degree)), np.sin(np.radians(degree))])

    def label(self, image_h_channel, c, size, bgr):
        mask = np.zeros(image_h_channel.shape[:2], dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)
        mask = cv2.erode(mask, None, iterations=2)
        b, g, r, m = cv2.mean(bgr, mask)
        h, s, v = cv2.split(cv2.cvtColor(
            np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV))
        vec_x = np.cos(np.radians(h.astype(np.uint16)*2))
        vec_y = np.sin(np.radians(h.astype(np.uint16)*2))
        mean_vector = np.array(
            [np.mean(vec_x), np.mean(vec_y)])
        mean_degree = np.degrees(np.arctan2(mean_vector[1], mean_vector[0]))
        minDist = (-1, None)
        if (np.isnan(mean_degree)):
            return "unidentified", 0
        for (i, vec) in enumerate(self.vectors):
            d = np.dot(vec, mean_vector)
            if d > minDist[0]:
                minDist = (d, i)
        return self.colorNames[minDist[1]], mean_degree

class CubeRecognizer:
    start_time=0
    def init(self,thresh_=140,dict_=None):
        self.thresh=thresh_
        self.cl=ColorLabeler(dict_)
        self.start_time=time()
    def get_rec_cen(self,image_original):
        image_hsv = cv2.cvtColor(image_original, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(image_hsv)
        thresh = cv2.threshold(s, self.thresh, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        cnts = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        rects = []
        for c in cnts:
            M = cv2.moments(c)
            if (M["m00"] == 0):
                continue
            cX = int((M["m10"] / M["m00"]))
            size = M["m00"]
            if (size > 300):
                color, deg = self.cl.label(h, c, size, image_original)
            else:
                color = "N/A"
                deg = "N/A"
            c = c.astype("int")
            x,y,width,height=cv2.boundingRect(c)
            if(size>80000):
                continue
            rects.append((cX, color, size, deg, height))
        rects = sorted(rects, key=lambda x: x[2], reverse=True)
        if rects:
            print(rects[0])
            return rects[0][0], rects[0][1], rects[0][2], rects[0][4]
        else:
            return 0, "red", 0, 0