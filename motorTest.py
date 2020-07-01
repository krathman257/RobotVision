import maestro
from picamera import PiCamera
from time import sleep

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

camera = PiCamera()
camera.start_preview()

tango = maestro.Controller()
tango.setTarget(BODY,6400)
tango.setTarget(HEADTILT,4100)
tango.setTarget(HEADTURN,6000)

sleep(10)
camera.stop_preview()
