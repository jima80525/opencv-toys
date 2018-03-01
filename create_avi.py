#!/usr/bin/env python3
import cv2
import numpy as np

def grey():
    writer = cv2.VideoWriter("grey.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))
    for frame in range(100):
        writer.write(np.full((480,640,3), 100).astype('uint8'))
    writer.release()

def color_noise():
    writer = cv2.VideoWriter("color_noise.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))
    for frame in range(100):
        writer.write(np.random.randint(0, 255, (480,640,3)).astype('uint8'))
    writer.release()

def rect():
    writer = cv2.VideoWriter("rect.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))
    for frame in range(100):
        img = np.zeros((480,640,3), np.uint8)
        cv2.rectangle(img,(frame,50),(frame+50,128),(255,255,0),-3)
        writer.write(img)

    writer.release()

def circle():
    writer = cv2.VideoWriter("circle.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30,(640,480))
    for frame in range(20):
        img = np.zeros((480,640,3), np.uint8)
        writer.write(img)

    for frame in range(600):
        img = np.zeros((480,640,3), np.uint8)
        if frame < 300:
            y = int(frame / 2)
        else:
            y = int(150 - (frame - 300) / 2)
        cv2.circle(img,(frame + 40, y + 50),30,(255,255,0),-3)
        writer.write(img)

    writer.release()


grey()
color_noise()
rect()
circle()
