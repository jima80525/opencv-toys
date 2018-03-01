#!/usr/bin/env python3
import cv2
import numpy
import sys

if len(sys.argv) < 2:
    filename = 'circle.avi'
else:
    filename = sys.argv[1]


cap = cv2.VideoCapture(filename)
fgbg = cv2.createBackgroundSubtractorMOG2()
# fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
# fgbg = cv2.bgsegm.createBackgroundSubtractorGSOC()
# fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()

while(1):
    ret, frame = cap.read()
    if not ret:
        break
    origframe = frame.copy()
    fgmask = fgbg.apply(frame)

    ret, thresh = cv2.threshold(fgmask, 240, 255, cv2.THRESH_BINARY)
    kernel = numpy.ones((5,5),numpy.uint8)
    dilation = cv2.dilate(thresh,kernel,iterations = 1)
    erosion = cv2.erode(thresh,kernel,iterations = 1)

    # contours = cv2.findContours(erosion, cv2.RETR_TREE,  cv2.CHAIN_APPROX_SIMPLE)
    (im2, contours, hierarchy) = cv2.findContours(erosion, 1, 2)

    for contour in contours:
        area = cv2.contourArea(contour)
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = numpy.int0(box)
        cv2.drawContours(frame,[box],0,(255,0,0),2)
    # cv2.imshow('mask',fgmask)
    cv2.imshow('frame',frame)
    cv2.imshow('original frame',origframe)
    # cv2.imshow('thresh',erosion)
    # cv2.imshow('frame',big)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
