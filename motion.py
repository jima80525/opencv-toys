#!/usr/bin/env python3
import cv2
import numpy

cap = cv2.VideoCapture('circle.avi')
# fgbg = cv2.createBackgroundSubtractorMOG2()
# fgbg = cv2.createBackgroundSubtractorGSOC()
fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()

while(1):
    ret, frame = cap.read()
    if not ret:
        break
    fgmask = fgbg.apply(frame)
    # big = numpy.hstack((frame, fgmask))
    # big = numpy.concatenate((frame, fgmask), axis = 1)
    cv2.imshow('mask',fgmask)
    cv2.imshow('frame',frame)
    # cv2.imshow('frame',big)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()
