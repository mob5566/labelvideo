"""
# Label tracking target in video

## Information

* Author: Cheng-Shih Wong
* Email:  mob5566@gmail.com

"""

from __future__ import print_function

import os
import sys
import time

import cv2
import numpy as np

usagemsg = "Usage: labelvideo.py <input_video> [<output_file_name> [label_file]]"
infomsg = "\
Use mouse left button to drag target bounding box\n\
Press 'q': quit\n\
Press 'e': target disappear\n\
Press 's': toggle stop/resume\n\
Press 'j': slow down\n\
Press 'k': speed up\n\
Press ' ': save the bounding box\n\

* Use one dash '-' as the output_file_name will not generate output file
"

drag_start = None
sel = None

def onmouse(event, x, y, flags, param):
  global drag_start, sel

  if event == cv2.EVENT_LBUTTONDOWN:
    drag_start = x, y
    sel = 0,0,0,0
  elif event == cv2.EVENT_LBUTTONUP:
    drag_start = None

  if drag_start:
    minpos = min(drag_start[0], x), min(drag_start[1], y)
    maxpos = max(drag_start[0], x), max(drag_start[1], y)
    sel = minpos[0], minpos[1], maxpos[0], maxpos[1]

if __name__ == '__main__':

  argv = sys.argv
  if len(argv) != 2 and len(argv) != 3 and len(argv) != 4:
    print(usagemsg)
    sys.exit(-1)
  else:
    ts = time.localtime()
    outfile = os.path.basename(argv[1])

    invideo = argv[1]

    if len(argv)>=3:
      outfile = argv[2]

    inlabel = argv[3] if len(argv)==4 else None

    if outfile != '-':
      outfile = '{}_{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}.txt'.format(outfile,
                    ts.tm_year, ts.tm_mon, ts.tm_mday,
                    ts.tm_hour, ts.tm_min, ts.tm_sec)
    
  # Initializing
  cap = cv2.VideoCapture(invideo)
  wn = 'Label video'
  cv2.namedWindow(wn)
  cv2.setMouseCallback(wn, onmouse)

  if not cap.isOpened():
    print("Video doesn't exist!")
    sys.exit(-1)

  if inlabel and not os.path.isfile(inlabel):
    print("Input labelled file doesn't exist!")
    sys.exit(-1)

  # Read the labelled bounding box
  if inlabel:
    bbx = []
    with open(inlabel, 'rb') as f:
      for line in f.readlines():
        bbx.append(map(int, line.split()))
    bbxn = len(bbx)

  # Get bounding box
  if inlabel and bbxn>=1:
    rect = bbx[0][1:]
    sel = None if rect[0]==-1 else rect
    if sel:
      sel = [v/2 for v in sel]

  # Show information
  print(infomsg)
  notend, curf = cap.read()
  fcnt = 1
  rois = []
  delayT = 30
  stop = True

  while notend:

    # Get current frame
    outf = curf.copy()
    outf = cv2.resize(outf, (outf.shape[1]/2, outf.shape[0]/2))

    # Draw output frame
    if sel:
      cv2.rectangle(outf, tuple(sel[:2]), tuple(sel[2:]), (255, 0, 0), 2)

    cv2.putText(outf, 'Frame {:5d}'.format(fcnt), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
    cv2.putText(outf, 'Delay {:5d}'.format(delayT), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

    # Show the result
    cv2.imshow(wn, outf)
    key = cv2.waitKey(delayT)&255

    if key==ord(' ') or not stop:
      notend, curf = cap.read()
      
      # Record the bounding box
      if sel:
        rois.append(sel)
      else:
        rois.append((-1, -1, -1, -1))
      fcnt += 1

      # Get bounding box
      if inlabel and fcnt <= bbxn:
        rect = bbx[fcnt-1][1:]
        sel = None if rect[0]==-1 else rect
        if sel:
          sel = [v/2 for v in sel]

    # Clean the bounding box
    if key==ord('e'):
      sel = None

    # Slow down or speed up video
    if key==ord('j'):
      delayT += 10

    if key==ord('k'):
      delayT -= 10

    # Stop playing
    if key==ord('s'):
      stop ^= True

    # Quit
    if key==ord('q'):
      cap.release()
      break

  # Write the result
  if outfile!='-':
    with open(outfile, 'wb') as f:
      for i, bbx in enumerate(rois, 1):
        f.write('{:5d} {:3d} {:3d} {:3d} {:3d}\n'.format(i, bbx[0]*2, bbx[1]*2, bbx[2]*2, bbx[3]*2))

  cv2.destroyAllWindows()
