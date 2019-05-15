#!/usr/bin/env python3
''' Basic idea lifted from here
https://stackoverflow.com/questions/2231518/how-to-read-a-frame-from-yuv-file-in-opencv/28210874
'''
import argparse
import cv2
import numpy as np


def readFrame(filename, width, height):
    with open(filename, 'rb') as fp:
        frame_len = int(width * height * 3 / 2)
        shape = (int(height*1.5), width)
        while True:
            raw = fp.read(frame_len)
            if not raw:
                break
            yuv = np.frombuffer(raw, dtype=np.uint8)
            yuv = yuv.reshape(shape)
            yield cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)


def readYFrame(filename, width, height):
    with open(filename, 'rb') as fp:
        frame_len = width * height
        extra_len = int(width * (height / 2))
        shape = (height, width)
        while True:
            raw = fp.read(frame_len)
            if not raw:
                break
            extra = fp.read(extra_len)
            yuv = np.frombuffer(raw, dtype=np.uint8)
            yuv = yuv.reshape(shape)
            yield yuv


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='name of yuv file to display')
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    width = 1024
    height = 576
    for frame in readYFrame(args.filename, width, height):
        cv2.imshow("frame", frame)
        cv2.waitKey(30)
