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
    parser.add_argument('-y', '--yuvfile', help='file of yuv stream frames')
    parser.add_argument('-d', '--show-dilation', action='store_true',
                        help='display mask after dilation')
    parser.add_argument('-e', '--show-erosion', action='store_true',
                        help='display mask after erosion')
    parser.add_argument('-m', '--show-mask', action='store_true',
                        help='display initial mask')
    parser.add_argument('-o', '--show-original', action='store_true',
                        help='display original image')
    parser.add_argument('--min-area', type=int, default=1000,
                        help='smallest object size')
    parser.add_argument('-r', '--show-rects', action='store_true',
                        help='show rects on output instead of cells')
    args = parser.parse_args()
    return args


class FileReader():
    def __init__(self, filename):
        self.cap = cv2.VideoCapture(filename)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame


class YuvReader():
    def __init__(self, filename):
        self.fp = open(filename, 'rb')
        # JHA TODO figure out how to deal with this
        self.width = 1024
        self.height = 576
        self.frame_len = self.width * self.height
        self.extra_len = int(self.width * (self.height / 2))
        self.shape = (self.height, self.width)

    def __del__(self):
        self.fp.close()

    def get_frame(self):
        while True:
            raw = self.fp.read(self.frame_len)
            if not raw:
                break
            extra = self.fp.read(self.extra_len)
            yuv = numpy.frombuffer(raw, dtype=numpy.uint8)
            yuv = yuv.reshape(self.shape)
            yield yuv


class CameraReader():
    def __init__(self, ip_addr):
        filename = 'rtsp://{}/stream1'.format(ip_addr)
        self.cap = cv2.VideoCapture(filename)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        while True:
            frames_to_skip = 10
            while frames_to_skip:
                ret, frame = self.cap.read()
                if not ret:
                    break
                frames_to_skip -= 1

            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame


class SAEngine:
    def __init__(self, width, height, args):
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.kernel = numpy.ones((5, 5), numpy.uint8)
        self.mask = Window('mask', args.show_mask)
        self.dilation = Window('dilation', args.show_dilation)
        self.erosion = Window('erosion', args.show_erosion)
        self.mask = Window('mask', args.show_mask)
        self.dilation = Window('dilation', args.show_dilation)
        self.erosion = Window('erosion', args.show_erosion)
        self.min_area = args.min_area

    def get_motion_rects(self, frame):
        fgmask = self.fgbg.apply(frame)

        self.mask.show(fgmask)

        # JHA TODO set flag for iterations?
        erosion_frame = cv2.erode(fgmask, self.kernel, iterations=2)
        dilation_frame = cv2.dilate(erosion_frame, self.kernel, iterations=2)
        self.dilation.show(dilation_frame)
        self.erosion.show(erosion_frame)

        (contours, hierarchy) = cv2.findContours(dilation_frame,
                                                 cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_NONE)

        rects = [cv2.boundingRect(contour) for contour in contours if
                 cv2.contourArea(contour) > self.min_area]
        return rects


def drawRects(frame, rects):
    """ Draws bounding boxes from motion detection. """
    for x, y, w, h in rects:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1)


def drawCells(frame, rects, width, height):
    """ Highlights the 16x16 pixel cells which contain motion. """
    def roundDown(val):
        return math.floor(val/16) * 16
    def roundUp(val):
        return math.ceil(val/16) * 16

    # draw grid
    for x in range(0, width, 16):
        cv2.line(frame, (x, 0), (x, height), (255, 0, 0))
    for y in range(0, height, 16):
        cv2.line(frame, (0, y), (width, y), (255, 0, 0))


    # create an overlay frame
    img = numpy.zeros((height, width), numpy.uint8)

    for x, y, w, h in rects:
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

def main():
    args = get_args()

    if args.filename:
        cap = FileReader(args.filename)
    elif args.yuvfile:
        cap = YuvReader(args.yuvfile)
        # JHA todo - cell drawing is based on 3 color frames.  For YUV we're
        # only doing Y field
        args.show_rects = True
    else:
        cap = CameraReader(args.ip_addr)

    Window.width = cap.width
    Window.height = cap.height

    original = Window('original frame', args.show_original)
    output = Window(f"Cell-based Motion ({Window.width}x{Window.height})", True)

    engine = SAEngine(cap.width, cap.height, args)

    for frame in cap.get_frame():

        original.show(frame)

        rects = engine.get_motion_rects(frame)

        if args.show_rects:
            drawRects(frame, rects)
        else:
            drawCells(frame, rects, cap.width, cap.height)

        output.show(frame)

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
# frame = cv2.resize(frame, (1024, 576), interpolation=cv2.INTER_AREA)
