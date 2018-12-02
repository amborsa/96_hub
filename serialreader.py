import serial
import datetime
import zmq
import time
from helpers import *

# code for reading serial
# while True:
# 	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
# 	ser.flushInput()
# 	serial_data = ser.readline()
# 	serial_string = serial_data.decode("utf-8")
#	some delay before next read
### this should end up returning the: node (id), time in milliseconds, heart rate, respiratory rate, temperature
### --> for each slave device

def main():
	## open up serial connection
	## open web socket
	## read/parse serial
	## send parsed serial data via web socket
	## receive alarm states, ages via web socket
	## send alarm states, ages via serial
	## wait some amount of time -- do it again

	while True:
		# open zmq port to communication with other programs
		context = zmq.Context()
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://localhost:5556")

		sent_data = "vital data"
		socket.send_string("vital data")
		print(sent_data)
		received_data = socket.recv_string()
		print(received_data)

		time.sleep(10)







	# # these are dummy variables
	# id = 3
	# ms = 24000000 # this is about 6.67 hours
	# our_time = 73.0
	# now = datetime.datetime.now()
	# then = now - datetime.timedelta(hours=0, minutes=ms/60000)
	# hr = 58.3
	# rr = 12.3
	# temp = 37.2

	# datapts = 72 # once an hour for three days

	# # in a loop
	# while True:
	# 	query = Vital.query.filter(Vital.id==id)
	# 	add_vital = Vital(id=id, time=our_time, datetime=then, hr=hr, rr=rr, temp=temp)
	# 	db.session.add(add_vital)
	# 	if query.count() > datapts:
	# 		db.session.delete(query.first())
	# 	db.session.commit()
	# 	time.sleep(1)
	# # end of loop




	# # after loop
	# db.session.commit()








if __name__ == "__main__":
	main()

