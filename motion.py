#!/usr/bin/env python3
import argparse
import cv2
import itertools
import math
import numpy


class Window():
    next_x_pos = 1800 # JHA hack to get it on big monitor at work
    next_y_pos = 20
    width = 0
    height = 0

    def __init__(self, title, visible):
        ''' The positioning of windows was not something I figured out.  Gave
        up as it wasn't worth the effort. '''
        self.visible = visible
        self.title = title
        if self.visible:
            print(title, self.width, self.next_x_pos, visible)
            # cv2.namedWindow(self.title, cv2.WINDOW_NORMAL)
            cv2.namedWindow(self.title, cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow(self.title, self.next_x_pos, self.next_y_pos)
            # print(f"Moving to {
            Window.next_x_pos += self.width + 3 # JHA TODO wrap if hit edge

    def show(self, frame):
        if self.visible:
            cv2.imshow(self.title, frame)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', help='video file to process')
    parser.add_argument('-i', '--ip_addr',
                        help='ip address from which to stream')
    parser.add_argument('-d', '--show-dilation', action='store_true',
                        help='display mask after dilation')
    parser.add_argument('-o', '--show-original', action='store_true',
                        help='display original image')
    parser.add_argument('-e', '--show-erosion', action='store_true',
                        help='display mask after erosion')
    parser.add_argument('-m', '--show-mask', action='store_true',
                        help='display initial mask')
    parser.add_argument('-r', '--rotate-rect', action='store_true',
                        help='allow bounding rectable to be angled')
    parser.add_argument('--min-area', type=int, default=1000,
                        help='smallest object size')
    args = parser.parse_args()
    return args


def get_background_subtractor(args):
    # JHA TODO add options for picking algorithm
    fgbg = cv2.createBackgroundSubtractorMOG2()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGSOC()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
    # fgbg = cv2.createBackgroundSubtractorCNT()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorLSBP()
    return fgbg


def get_frame(cap, frames_to_skip):
    while frames_to_skip:
        ret, frame = cap.read()
        if not ret:
            return None, None
        frames_to_skip -= 1

    return cap.read()


def main():
    args = get_args()

    fgbg = get_background_subtractor(args)
    if args.filename:
        filename = args.filename
        skip_frames = 0
    else:
        filename = 'rtsp://{}/stream1'.format(args.ip_addr)
        skip_frames = 10

    cap = cv2.VideoCapture(filename)

    Window.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    Window.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    original = Window('original frame', args.show_original)
    output = Window(f"Cell-based Motion ({Window.width}x{Window.height})", True)
    mask = Window('mask', args.show_mask)
    dilation = Window('dilation', args.show_dilation)
    erosion = Window('erosion', args.show_erosion)

    kernel = numpy.ones((5, 5), numpy.uint8)

    for loop_count in itertools.count():
        ret, frame = get_frame(cap, skip_frames)
        if not ret:
            break

        # frame = cv2.resize(frame, (1024, 576), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, (426, 240), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, (480, 640), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_AREA)

        original.show(frame)
        fgmask = fgbg.apply(frame)
        mask.show(fgmask)

        if False:
            dilation_frame = cv2.dilate(fgmask, kernel, iterations=2)
            erosion_frame = cv2.erode(dilation_frame, kernel, iterations=2)
        else:
            erosion_frame = cv2.erode(fgmask, kernel, iterations=2)
            dilation_frame = cv2.dilate(erosion_frame, kernel, iterations=2)

        (contours, hierarchy) = cv2.findContours(erosion_frame,
                                                 cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_NONE)

        img = numpy.zeros(erosion_frame.shape, numpy.uint8)
        def roundDown(val):
            return math.floor(val/16) * 16
        def roundUp(val):
            return math.ceil(val/16) * 16

        # draw grid
        h, w = erosion_frame.shape
        for x in range(0, w, 16):
            cv2.line(frame, (x, 0), (x, h), (255, 0, 0))
        for y in range(0, h, 16):
            cv2.line(frame, (0, y), (w, y), (255, 0, 0))


        for contour in contours:
            area = cv2.contourArea(contour)
            if area > args.min_area:
                if args.rotate_rect:
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
                    box = numpy.int0(box)
                    cv2.drawContours(frame, [box], 0, (255, 0, 0), 2)
                else:
                    x, y, w, h = cv2.boundingRect(contour)
                    # draw the orig rect on the frame
                    # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1)

                    # now draw the cells on the overlay frame
                    x0 = roundDown(x)
                    y0 = roundDown(y)
                    x1 = roundUp(x + w)
                    y1 = roundUp(y + h)

                    cv2.rectangle(img, (x0, y0), (x1, y1), (255, 0, 0), -3)

        #####
        # from:
        # https://stackoverflow.com/questions/46103731/is-there-a-simple-method-to-highlight-the-mask/46105196#46105196
        b,g,r = cv2.split(frame)
        g = cv2.add(g, 90, dst = g, mask = img, dtype = cv2.CV_8U)
        cv2.merge((b,g,r), frame)
        #####

        output.show(frame)
        dilation.show(dilation_frame)
        erosion.show(erosion_frame)
        # input()
        # print("new frame")

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
