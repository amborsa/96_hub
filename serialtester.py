from serial import Serial
import datetime
import zmq
import time
import random
import sys

def main():
	if int(sys.argv[1]) == 0:
		ser = Serial('/dev/ttyACM0', 9600, timeout=1)
		ser.Begin()
		ser.flushInput()
		serial_data = ser.readline()
		serial_string = serial_data.decode("utf-8")
		print(serial_data)	
	elif int(sys.argv[1]) == 1:
		# serial simulation
		serial_array = [random.randint(1,4), random.uniform(1000,10000), random.uniform(50,100), random.uniform(12,15), \
		random.uniform(36, 39)]
		serial = ",".join(str(round(e,1)) for e in serial_array)
	elif int(sys.argv[1]) == 2:
		return 0
	else:
		return 1

if __name__ == "__main__":
	main()