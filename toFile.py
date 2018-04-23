#!/usr/bin/env python3
''' Basic idea lifted from here
https://stackoverflow.com/questions/2231518/how-to-read-a-frame-from-yuv-file-in-opencv/28210874
'''
import argparse
import cv2
import numpy as np


def writeFrame(fp, bgr, width, height):
    # convert bgr to YUV444
    yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)

    # split out and resize the chroma channels
    y, u, v = cv2.split(yuv)
    u = cv2.resize(u, (int(width/2), int(height/2)))
    v = cv2.resize(v, (int(width/2), int(height/2)))

    # interleave the chroma channels
    w, x = np.ravel(u), np.ravel(v)
    rows = u.shape[0]
    z = np.ravel([z for z in zip(x, w)]).reshape(rows, -1)

    # write out this frame
    y.tofile(fp)
    z.tofile(fp)


def rectGenerator(num_frames, width, height):
    for frame in range(num_frames):
        img = np.zeros((height, width, 3), np.uint8)
        cv2.rectangle(img, (frame, 50), (frame+50, 128), (255, 255, 0), -3)
        yield img


def circleGenerator(num_frames, width, height):
    for frame in range(num_frames - 20):
        img = np.zeros((height, width, 3), np.uint8)
        if frame < num_frames / 2:
            y = int(frame / 2)
        else:
            y = int((num_frames / 2) - (frame / 2))
        cv2.circle(img, (frame + 40, y + 50), 30, (255, 0, 0), -3)
        yield img


def fileGenerator(filename, width, height):
    cap = cv2.VideoCapture(filename)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', help='name of yuv file to write',
                        default='output.yuv')
    parser.add_argument('-n', '--numframes', help='number of frames to write',
                        default=100)
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('-f', '--infile', nargs='?',
                     help='name of yuv file to read')
    grp.add_argument('-r', '--rectangle', action='store_true',
                     help='generate a rectangle instead of a circle')

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    print(args)
    width, height = (1024, 576)

    # JHA the first_arg business is a bit of a hack.  The file generator takes
    # a very different first param than the circle or rect generators do.
    if (args.infile):
        generator = fileGenerator
        first_arg = args.infile
    elif (args.rectangle):
        generator = rectGenerator
        first_arg = int(args.numframes)
    else:
        generator = circleGenerator
        first_arg = int(args.numframes)

    with open(args.outfile, 'wb') as fp:
        for img in generator(first_arg, width, height):
            cv2.imshow("frame", img)
            writeFrame(fp, img, width, height)
            cv2.waitKey(30)
