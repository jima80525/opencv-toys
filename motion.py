#!/usr/bin/env python3
import argparse
import cv2
import numpy
import sys

class Window():
    next_x_pos = 20
    next_y_pos = 20
    width = 0
    height = 0

    def __init__(self, title, visible):
        self.visible = visible
        self.title = title
        if self.visible:
            cv2.namedWindow(self.title)
            cv2.moveWindow(self.title, self.next_x_pos, self.next_y_pos)
            Window.next_x_pos += self.width  # JHA TODO wrap if hit end of screen?

    def show(self, frame):
        if self.visible:
            cv2.imshow(self.title, frame)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help='video files to process')
    parser.add_argument('-t', '--threshold', action='store_true', 
                        help='apply thresholding limit')
    parser.add_argument("-l", "--limit", type=int, default=0,
                        help='threshold limit, only used with -t')
    parser.add_argument('-d', '--show-dilation', action='store_true',
                        help='display mask after dilation')
    parser.add_argument('-e', '--show-erosion', action='store_true',
                        help='display mask after erosion')
    parser.add_argument('-r', '--rotate-rect', action='store_true',
                        help='allow bounding rectable to be angled')
    parser.add_argument('-m', '--min-area', type=int, default=10,
                        help='smallest object size')
    args = parser.parse_args()
    return args

def get_background_subtractor(args):
    # JHA TODO add options for picking algorithm
    fgbg = cv2.createBackgroundSubtractorMOG2()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGSOC()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorLSBP()
    return fgbg


def main():
    args = get_args()
                        
    fgbg = get_background_subtractor(args)

    cap = cv2.VideoCapture(args.filename)

    Window.width = int(cap.get(3)) 
    Window.height = int(cap.get(4)) 
    
    args = parser.parse_args()
    return args

def get_background_subtractor(args):
    # JHA TODO add options for picking algorithm
    # fgbg = cv2.createBackgroundSubtractorMOG2()
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGSOC()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()
    # fgbg = cv2.bgsegm.createBackgroundSubtractorLSBP()
    return fgbg


def main():
    args = get_args()
                        
    fgbg = get_background_subtractor(args)

    cap = cv2.VideoCapture(args.filename)

    Window.width = int(cap.get(3)) 
    Window.height = int(cap.get(4)) 
    
    original = Window('original frame', True)
    output = Window('output', True)
    dilation = Window('dilation', args.show_dilation)
    erosion = Window('erosion', args.show_erosion)

    kernel = numpy.ones((5,5),numpy.uint8)

    while(1):
        ret, frame = cap.read()
        if not ret:
            break
    
        origframe = frame.copy()
        fgmask = fgbg.apply(frame)
    
        if args.threshold:
            ret, fgmask = cv2.threshold(fgmask, args.limit, 255, cv2.THRESH_BINARY)

        dilation_frame = cv2.dilate(fgmask,kernel,iterations = 1)
        erosion_frame = cv2.erode(dilation_frame,kernel,iterations = 1)
    
        (im2, contours, hierarchy) = cv2.findContours(erosion_frame, cv2.RETR_EXTERNAL,  cv2.CHAIN_APPROX_SIMPLE)
    
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > args.min_area:
                if args.rotate_rect:
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
                    box = numpy.int0(box)
                    cv2.drawContours(frame,[box],0,(255,0,0),2)
                else:
                    x,y,w,h = cv2.boundingRect(contour)
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        original.show(origframe)
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
