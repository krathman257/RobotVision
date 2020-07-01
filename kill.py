import maestro

tango = maestro.Controller()

MOTORS = 1
TURN = 2
BODY = 0
HEADTILT = 4
HEADTURN = 3

tango.setTarget(MOTORS, 6000)
tango.setTarget(TURN, 6000)
tango.setTarget(BODY, 6000)
tango.setTarget(HEADTILT, 6000)
tango.setTarget(HEADTURN, 6000)

tango.close()
