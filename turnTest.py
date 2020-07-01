import maestro
import time

TURN = 2
HEADTURN = 3

tango = maestro.Controller()

tango.setTarget(3, 6000)

print(tango.getPosition(3))
