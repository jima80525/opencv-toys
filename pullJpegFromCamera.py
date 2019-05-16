#!/usr/bin/env python3
import argparse
import cv2
import itertools
import numpy
import urllib.request


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
            Window.next_x_pos = 3300

    def show(self, frame):
        if self.visible:
            cv2.imshow(self.title, frame)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', help='ip address from which to stream')
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    jpegname = 'http://{}/jpeg?id=131'.format(args.ip_addr)
    ive = Window('IVE algorithm', jpegname)
    # skip_frames = 10

    for loop_count in itertools.count():
        # if not loop_count % skip_frames:
        url_response = urllib.request.urlopen(jpegname)
        img_array = numpy.array(bytearray(url_response.read()),
                                dtype=numpy.uint8)
        img = cv2.imdecode(img_array, -1)
        ive.show(img)

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
