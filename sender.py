import zmq
import time

# open zmq port to communication with other programs
context = zmq.Context()
# socket = context.socket(zmq.PUB)
socket = context.socket(zmq.REQ)
# socket.bind("tcp://*:5556") # was "tcp://*:5556" earlier
socket.connect("tcp://localhost:5556")

def change_this():
    socket.send_string("test")
    print("sent something")
    # socket.send_string("test2")
    # socket.send_string("test3")
    # socket.send_string("test4")
    # socket.send_string("test5")
    print(socket.recv_string())

print("Beginning keylogging and transmitting data...")  

while True:
	change_this()
	time.sleep(5)


print("Quitting keylogger...")