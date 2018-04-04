#!/usr/bin/env python3
import argparse
import cv2
import itertools
import numpy


class Window():
    next_x_pos = 1800
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
            # Window.next_x_pos += self.width  # JHA TODO wrap if hit edge
            Window.next_x_pos = 3300

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
    parser.add_argument('-k', '--show-mask', action='store_true',
                        help='display initial mask')
    parser.add_argument('-r', '--rotate-rect', action='store_true',
                        help='allow bounding rectable to be angled')
    parser.add_argument('-m', '--min-area', type=int, default=1000,
                        help='smallest object size')
    args = parser.parse_args()
    return args


def get_background_subtractor(args):
    # JHA TODO add options for picking algorithm
    # fgbg = cv2.createBackgroundSubtractorMOG2()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGSOC()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
    fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()
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
    output = Window('OpenCV algorithm', True)
    dilation = Window('dilation', args.show_dilation)
    erosion = Window('erosion', args.show_erosion)
    mask = Window('mask', args.show_mask)

    kernel = numpy.ones((5, 5), numpy.uint8)

    for loop_count in itertools.count():
        ret, frame = get_frame(cap, skip_frames)
        if not ret:
            break

        frame = cv2.resize(frame, (1024, 576), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, (426, 240), interpolation=cv2.INTER_AREA)

        # frame = cv2.resize(frame, (480, 640), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
        # frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_AREA)

        original.show(frame)
        fgmask = fgbg.apply(frame)
        mask.show(fgmask)

        dilation_frame = cv2.dilate(fgmask, kernel, iterations=1)
        erosion_frame = cv2.erode(dilation_frame, kernel, iterations=1)

        (im2, contours, hierarchy) = cv2.findContours(erosion_frame,
                                                      cv2.RETR_EXTERNAL,
                                                      cv2.CHAIN_APPROX_SIMPLE)

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
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        output.show(frame)
        dilation.show(dilation_frame)
        erosion.show(erosion_frame)

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
