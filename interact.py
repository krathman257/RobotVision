from ClientSocket import ClientSocket
from threading import Thread
from threading import Timer
import cv2 as cv
import maestro
import numpy as np
import mpmath
import time
from picamera import PiCamera
from picamera.array import PiRGBArray

#Variables
IP = '10.200.8.58'
PORT = 5010
client = ClientSocket(IP, PORT)
waitTime = 3
left = False
lossTime = 0
prevFaceFound = False
centerStep = 200
centerXThresh = 25
centerYThresh = 25
faceDistTarget = 12
ANGULAR_VELOCITY = 2000
VELOCITY = 0.2
headX = 6000
headY = 6000
HEADTILT = 4
HEADTURN = 3
WAIST = 0
TURN = 2
MOTORS = 1
tango = maestro.Controller()

#Move forward, backward, left or right for s seconds
def moveLeft(s):
	tango.setTarget(TURN, 7000)
	time.sleep(s)
	tango.setTarget(TURN, 6000)

def moveRight(s):
	tango.setTarget(TURN, 5000)
	time.sleep(s)
	tango.setTarget(TURN, 6000)

def moveForward(s):
	tango.setTarget(MOTORS, 5000)
	time.sleep(s)
	tango.setTarget(MOTORS, 6000)

def moveBack(s):
	tango.setTarget(MOTORS, 7000)
	time.sleep(s)
	tango.setTarget(MOTORS, 6000)

#Center camera on detected face (incremental, once per frame)
def centerOnFace(x,y):
	global headX, headY, HEADTILT, HEADTURN
	if x < 320:
		headX += int(centerStep * (x/320))
		tango.setTarget(HEADTURN,headX)
	if x > 320:
		headX -= int(centerStep * ((x-320)/320))
		tango.setTarget(HEADTURN,headX)
	if y < 240:
		headY += int(centerStep * (y/240))
		tango.setTarget(HEADTILT,headY)
	if y > 240:
		headY -= int(centerStep * ((y-240)/240))
		tango.setTarget(HEADTILT,headY)

#Returns true if face is within center threshhold (centerXThresh and centerYThresh)
def isCentered(x,y):
	return 320-centerXThresh < x and x < 320+centerXThresh and 240-centerYThresh < y and y < 240+centerYThresh

#Returns true if robot should search for a face
def shouldSearch():
	global lossTime
	return (time.time() - lossTime) > waitTime

#Moves the robot to center on a face, runs as a thread
def move(headX, faceWidth):

	#Rotate robot
	moveTime = abs(6000 - headX) / ANGULAR_VELOCITY

	if headX < 6000:
		moveRight(moveTime)
	elif headX > 6000:
		moveLeft(moveTime)

	#Move robot
	dist = mpmath.cot(mpmath.radians(62.2 * (w / 640) / 2))
	moveTime = abs(dist - faceDistTarget) * VELOCITY

	if dist < faceDistTarget:
		moveBack(moveTime)
	elif dist > faceDistTarget:
		moveForward(moveTime)

	client.sendData("Are you Sarah Connor?")

#Set PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.1)

#Set head servos to default
tango.setTarget(HEADTILT, headY)
tango.setTarget(HEADTURN, headX)
tango.setTarget(WAIST, 6000)

#Get face cascade
face_cascade = cv.CascadeClassifier("haarcascade.xml")

#For every frame
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	image = frame.array

	#Detect faces
	faces = face_cascade.detectMultiScale(image, 1.3, 5)

	#If last frame had face, current doesn't, set lossTime
	if prevFaceFound and len(faces) < 1:
		lossTime = time.time()

	#If no faces detected, and waitTime has passed, search
	if len(faces) < 1 and shouldSearch():
		tango.setTarget(HEADTILT, headY)
		if left:
			headX += 200
			tango.setTarget(HEADTURN,headX)
			if headX > 8000:
				left = False
				headY = 6000
				tango.setTarget(HEADTILT,headY)
		else:
			headX -= 200
			tango.setTarget(HEADTURN,headX)
			if headX < 4000:
				left = True
				headY = 6750
				tango.setTarget(HEADTILT,headY)

	#If faces detected
	if len(faces) > 0:
		(x,y,w,h) = faces[0]
		cv.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
		faceCenterX = x+w/2
		faceCenterY = y+h/2

		#If first frame of detected face, then greet, start move thread
		if not prevFaceFound and  shouldSearch() and len(faces) > 0:
			move_t = Thread(target=move, args=(headX, w))
			move_t.start()
			headX = 6000
			tango.setTarget(HEADTURN, headX)

		#If face isn't centered, center face with neck
		if not isCentered(faceCenterX, faceCenterY):
			centerOnFace(faceCenterX, faceCenterY)

	#Remember presence of faces in previous (this) frame
	prevFaceFound = len(faces) > 0

#	cv.imshow("Frame", image)
	cv.waitKey(1)
	rawCapture.truncate(0)
