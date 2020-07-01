import maestro
import time

HEADTILT = 4
HEADTURN = 3

tango = maestro.Controller()
tango.setTarget(HEADTILT,6000)

def search():
	while True:
		for x in range(0,4000,5):
			tango.setTarget(HEADTURN,4000+x)
			time.sleep(0.005)
		for x in range(0,4000,5):
			tango.setTarget(HEADTURN,8000-x)
			time.sleep(0.005)
search()
