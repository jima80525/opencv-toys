#!/usr/bin/env python3
''' Basic idea lifted from here
https://stackoverflow.com/questions/2231518/how-to-read-a-frame-from-yuv-file-in-opencv/28210874
'''
import argparse
import cv2
import numpy as np


def readFrame(fp, frame_len, shape):
    while fp.read(frame_len):
        raw = fp.read(frame_len)
        yuv = np.frombuffer(raw, dtype=np.uint8)
        yuv = yuv.reshape(shape)
        yield cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='name of yuv file to display')
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    width = 1024
    height = 576
    frame_len = int(width * height * 3 / 2)
    shape = (int(height*1.5), width)

    with open(args.filename, 'rb') as fp:
        for frame in readFrame(fp, frame_len, shape):
            cv2.imshow("frame", frame)
            cv2.waitKey(30)
