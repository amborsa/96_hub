from serial import Serial
import datetime
import zmq
import time
import random
import sys

def main():
	## open up serial connection
	## open web socket
	## read/parse serial --> will be receiving "{node},{delay (ms)},{hr},{rr},{temp}"
	## send parsed serial data via web socket
	## receive alarm states, ages via web socket
	## send alarm states, ages via serial
	## wait some amount of time -- do it again

	while True:
		if int(sys.argv[1]) == 0:
			exp_str = ""
			while True:
				ser = Serial('/dev/ttyACM0', 9600, timeout=1)
				ser.flushInput()
				serial_data = ser.readline()
				serial_string = serial_data.decode("utf-8")
				exp_str = serial_string.replace("\n", "")
				exp_str = exp_str.replace("\r", "")
				print(exp_str)
				# we need to further ensure we have what we want --> specify the length of this string
				if len(exp_str) == 26:
					print(len(exp_str))
					break
		elif int(sys.argv[1]) == 1:
			# serial simulation
			serial_array = [random.randint(1,4), random.uniform(1000,10000), random.uniform(50,100), random.uniform(12,15), \
			random.uniform(36, 39)]
			serial = ",".join(str(round(e,1)) for e in serial_array)
		elif int(sys.argv[1]) == 2:
			return 0
		else:
			return 1

		# open zmq port to communication with other programs
		context = zmq.Context()
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://localhost:5556")

		sent_data = exp_str
		socket.send_string(sent_data)
		received_data = socket.recv_string()
		print(received_data)

		# if int(sys.argv[1]) == 0:
		# 	ser.write(received_data)

		time.sleep(10)

if __name__ == "__main__":
	main()

