"""
# Verify the labels in video

## Information

* Author: Cheng-Shih Wong
* Email:  mob5566@gmail.com

"""

from __future__ import print_function

import os
import sys

import cv2
import numpy as np

usagemsg = "Usage: verifylabel.py <input_video> <input_label_file>"

if __name__ == '__main__':

  argv = sys.argv
  if len(argv) != 3:
    print(usagemsg)
    sys.exit(-1)

  invideo = sys.argv[1]
  inlabel = sys.argv[2]
    
  # Initializing
  cap = cv2.VideoCapture(invideo)
  wn = 'Label video'
  cv2.namedWindow(wn)

  if not cap.isOpened():
    print("Video doesn't exist!")
    sys.exit(-1)

  if not os.path.isfile(inlabel):
    print("Input labelled file doesn't exist!")
    sys.exit(-1)

  bbx = []
  with open(inlabel, 'rb') as f:
    for line in f.readlines():
      bbx.append(map(int, line.split()))
  bbxn = len(bbx)

  notend, curf = cap.read()
  fcnt = 0
  stop = False

  while notend:

    # Get current frame
    outf = curf.copy()
    outf = cv2.resize(outf, (outf.shape[1]/2, outf.shape[0]/2))

    # Show the result
    
    rect = bbx[fcnt%bbxn]
    if rect[1]!=-1:
      cv2.rectangle(outf, (rect[1]/2, rect[2]/2), (rect[3]/2, rect[4]/2), (255, 0, 0), 2)

    cv2.putText(outf, '{:5d}'.format(fcnt+1), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

    cv2.imshow(wn, outf)
    key = cv2.waitKey(10)&255

    if not stop:
      notend, curf = cap.read()
      fcnt += 1

    # Stop
    if key==ord('s'):
      stop ^= True

    # Quit
    if key==ord('q'):
      cap.release()
      break

  cv2.destroyAllWindows()
