from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import cv2

th1 = 50
th2 = 200

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	img = frame.array
	h,w,_ = img.shape
	img = img[int(h*4//5):,int(w//4):int(w*3//4)]
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = cv2.equalizeHist(img)
	img = cv2.GaussianBlur(img, (5,5), 10)
#	img = cv2.Canny(img, th1, th2)
	_,img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

	cv2.imshow("Frame", img)

	key = cv2.waitKey(1) & 0xFF
	rawCapture.truncate(0)
	if key == ord("q"):
		break
