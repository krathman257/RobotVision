import time
import maestro
import numpy as np
import cv2 as cv
from picamera import PiCamera
from picamera.array import PiRGBArray

#constants

lowest = 1000000000

#tango variables
MOTORS = 1
TURN = 2
WAIST = 0
HEADTILT = 4
HEADTURN = 3
#initial motor speed
MOTOR_SPEED = 5100
#binary image thresholds
THRESH_LOW=225
THRESH_HIGH=255
#maximum turn speed in either direction
TURN_RANGE=1500
#Minimum number of pixels of road before stopping
MIN_ROAD_PIXELS=20000

#initialize robot position
tango = maestro.Controller()
tango.setTarget(WAIST,6000)
tango.setTarget(HEADTILT,4000)
tango.setTarget(HEADTURN,6000)

#load camera image
camera = PiCamera()
camera.framerate = 32
camera.resolution = (640, 480)
img = PiRGBArray(camera, (640, 480))
time.sleep(0.1)

#start the robot going forward
tango.setTarget(MOTORS, MOTOR_SPEED)

#process image and move once each step
for frame in camera.capture_continuous(img, format="bgr", use_video_port=True):

   #grab frame image and dimensions
   image = frame.array
   h,w,_ = image.shape
   
   #crop image to bottom fifth and middle half
   image = image[int(h*2//3):,int(w//3):int(w*2//3)]
   h,w,_ = image.shape
   
   #create black and white mask to isolate road
   image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
   image = cv.equalizeHist(image)
   image = cv.GaussianBlur(image, (5,5) ,10)
   _,image = cv.threshold(image, THRESH_LOW, THRESH_HIGH, cv.THRESH_BINARY)

   #calculate Center of Gravity
   M = cv.moments(image)
   if M["m00"] != 0:
      cx = int(M["m10"] / M["m00"])
      cy = int(M["m01"] / M["m00"])
   else:
      cx = 0
      cy = 0
      
   #draw circle on COG
   #cv.circle(image,(cx,cy),10,0,2)
   
   #TODO: FIX FOR CONTINUOUS
   #calculate a turn speed in the range 5000 to 7000 based on COG's horizontal position
   turnSpeed = int(6000 + -1 * (((cx - (w/2)) / (w/2)) * TURN_RANGE)) #NOTE: upon testing make sure it turns correctly, or it might need a negative sign.

   #turn if the robot is about to go off the road
   tango.setTarget(TURN, turnSpeed)
   
   #print(M["m00"]) ##print number of white pixels
   
   img.truncate(0)

   #stop executing if there is no more road
   if M["m00"] < lowest:
      lowest = M["m00"]
      print(str(lowest))
   #print(str(M["m00"]))
   if M["m00"] < MIN_ROAD_PIXELS:
      break

#stop all motors
print("STOP")
tango.setTarget(MOTORS, 6000)
tango.setTarget(TURN, 6000)
