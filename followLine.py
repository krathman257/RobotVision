import time
import maestro
import numpy as np
import cv2 as cv
from picamera import PiCamera
from picamera.array import PiRGBArray

turnThresh = 0.05
turnMult = 1

#load tango variables
MOTORS = 1
TURN = 2
WAIST = 0
HEADTILT = 4
HEADTURN = 3

tango = maestro.Controller()
tango.setTarget(WAIST,5000)
tango.setTarget(HEADTILT,4000)
tango.setTarget(HEADTURN,6000)

#load camera image
camera = PiCamera()
camera.framerate = 32
camera.resolution = (640, 480)
img = PiRGBArray(camera, (640, 480))
time.sleep(0.1)

#process image
for frame in camera.capture_continuous(img, format="bgr", use_video_port=True):

   #grab frame
   image = frame.array
   h,w,_ = image.shape
   image = image[int(h*4//5):,int(w//4):int(w*3//4)]
   h,w,_ = image.shape
   image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
   image = cv.equalizeHist(image)
   image = cv.GaussianBlur(image, (5,5) ,10)
   _,image = cv.threshold(image, 225, 255, cv.THRESH_BINARY)

   M = cv.moments(image)
   if M["m00"] != 0:
      cx = int(M["m10"] / M["m00"])
      cy = int(M["m01"] / M["m00"])
   else:
      cx = 0
      cy = 0
   cv.circle(image,(cx,cy),10,0,2)
   #cv.imshow("Frame", image)
   #determine from processed image where the road is
   #print(str(cx) + ", " + str(cy))
   #stop if there is no more road

   turnTime = (((w/2) - cx) / (w/2)) * turnMult
   #print(turnTime)

   if turnTime >= turnThresh:
      tango.setTarget(TURN,7000)
      time.sleep(abs(turnTime))
      tango.setTarget(TURN,6000)

   if turnTime <= (turnThresh * -1):
      tango.setTarget(TURN,5000)
      time.sleep(abs(turnTime))
      tango.setTarget(TURN,6000)
  
   time.sleep(0.5)
   tango.setTarget(MOTORS,5200)
   time.sleep(1)
   tango.setTarget(MOTORS,6000)
   time.sleep(0.5)
   #turn if the robot is about to go off the road
   print(M["m00"])
   if M["m00"] < 200000:
      break
   #exit on pressing the q key
   key = cv.waitKey(1) & 0xFF
   #cv.imshow("Frame", image)
   img.truncate(0)
   if key == ord("q"):
      break

tango.setTarget(MOTORS, 6000)
tango.setTarget(TURN, 6000)
