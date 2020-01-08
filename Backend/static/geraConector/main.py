#!/usr/bin/env python

'''
Watershed segmentation
=========

This program demonstrates the watershed segmentation algorithm
in OpenCV: watershed().

Usage
-----
watershed.py [image filename]

Keys
----
  1-7   - switch marker color
  SPACE - update segmentation
  r     - reset
  a     - toggle autoupdate
  ESC   - exit

'''



# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv
import os
from os import path

import imageio
radius = 20

def on_trackbar(val):
    pt = (200, 200)
    blank_image = np.zeros((640,480,3), np.uint8)   
    cv.circle(blank_image, pt, int(val), (0 ,255, 0), 3)
    cv.imshow("Redondo", blank_image)



class Sketcher:
    def __init__(self, windowname, dests):
        self.windowname = windowname
        self.path = 0
        self.dests = dests
        self.inseridos = []
        cv.createTrackbar('R',self.windowname , 0, 255, on_trackbar)
        self.show()
        cv.setMouseCallback(self.windowname, self.on_mouse)

    def show(self):
        cv.imshow(self.windowname, self.dests)

    def on_mouse(self, event, x, y, flags, param):
        
        if event == cv.EVENT_LBUTTONDOWN:            
            h = 25
            w = 25
            images=[]
            crop_img = self.dests[y-h:y+h, x-w:x+w]
            gray = self.dests.copy()
            gray_crop = crop_img.copy()
            realce = self.dests.copy()
            realce[y-h:y+h, x-w:x+w] = crop_img
            if not os.path.exists("output/"+self.windowname):
                os.mkdir("output/"+self.windowname)
            global radius            
            pt = (x, y)
            realce = cv.circle(realce, pt, radius, (0,0,255), 3)
            #gray2 = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
            for ptAnt in self.inseridos:
                realce = cv.circle(realce, ptAnt, radius, (0,255,0), 3)                
                gray = cv.circle(gray, ptAnt, radius, (0,255,0), 3)
            self.inseridos.append(pt)
            dim=(1024,600)
            gray = cv.cvtColor(gray, cv.COLOR_BGR2RGB)
            realce = cv.cvtColor(realce, cv.COLOR_BGR2RGB)
            gray = cv.resize(gray, dim, interpolation = cv.INTER_AREA)
            realce = cv.resize(realce, dim, interpolation = cv.INTER_AREA)
            images.append(gray)
            images.append(realce)
            imageio.mimsave("output/"+self.windowname+"/"+str(self.path)+".gif",images)
                
            #cv.imshow("crop",realce)
            print("done")
            self.path += 1

           
            

       
class App:
    def __init__(self):
        global radius        
        path = "/home/pi/input"
        self.files = []
        self.filePointer = 0
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if '.jpg' in file:
                    self.files.append(file)
        print(self.files)
        self.img = cv.imread("input/"+self.files[0])
        if self.img is None:
            raise Exception('Failed to load image file: %s' % fn)

        h, w = self.img.shape[:2]     
        self.sketch = Sketcher(self.files[self.filePointer], self.img)



    def run(self):
        while 1:
            ch = cv.waitKey(20)
            if ch == 27:
                break
            if ch in [ord('n'), ord('N')]:
                on_trackbar(radius)
                self.filePointer += 1
                cv.destroyAllWindows()
                pathe = "input/"+self.files[self.filePointer]
                print(pathe)
                self.img = cv.imread(pathe)
                self.sketch = Sketcher(self.files[self.filePointer], self.img)
            if ch in [ord('a'), ord('A')]:
                global radius 
                radius -= 1
                on_trackbar(radius)
                print (radius)
            if ch in [ord('s'), ord('S')]:
                global radius 
                radius += 1
                on_trackbar(radius)
                print (radius)
       

        cv.destroyAllWindows()


if __name__ == '__main__':
    print(__doc__)
    import sys
    try:
        fn = sys.argv[1]
    except:
        fn = 'conector.jpg'
    App().run()