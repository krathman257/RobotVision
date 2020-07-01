from ClientSocket import ClientSocket
import time
import sys as s

IP = '10.200.50.10'
PORT = 5010

client = ClientSocket(IP, PORT)

if len(s.argv) < 2:
	print("No args, default used")
	client.sendData("This was a triumph. I'm making a note here, huge success.")

if len(s.argv) >= 2:
	for s in s.argv[1:]:
		client.sendData(str(s))
		time.sleep(2)

time.sleep(1)

client.killSocket()
