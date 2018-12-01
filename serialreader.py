import serial
import datetime
import time
from helpers import *

# importing Python package dependencies
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from tempfile import gettempdir
import random

''' Initializing App and Database '''
app = Flask(__name__)

# tries to ensure that caches aren't stored
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {
    'vitals': 'sqlite:///vitals.db',
    'inputs': 'sqlite:///input.db'
}
db = SQLAlchemy(app)

''' Defining Database Objects '''
# fields: entry id (unique), device id, time, hr, rr, temp
# NOTE: there is also a date datatype (potentially for time)
class Vital(db.Model):
    __bind_key__ = "vitals"
    e_id = db.Column('e_id', db.Integer, primary_key=True)
    id = db.Column('id', db.Integer, unique=False)
    time = db.Column('time', db.Float, unique=False)
    datetime = db.Column('datetime', db.DateTime, unique=False)
    hr = db.Column('hr', db.Float, unique=False)
    rr = db.Column('rr', db.Float, unique=False)
    temp = db.Column('temp', db.Float, unique=False)

# fields: device id (unique), name, hr threshold, rr threshold, temp threshold, alarm state
class Input(db.Model):
    __bind_key__ = "inputs"
    id = db.Column('id', db.Integer, primary_key=True)
    node = db.Column('node', db.Integer, unique=False)
    name = db.Column('name', db.String(30), unique=False)
    loc = db.Column('loc', db.String(30), unique=False)
    dob = db.Column('dob', db.String(10), unique=False)
    hr_thresh_high = db.Column('hr_thresh_high', db.Float, unique=False)
    rr_thresh_high = db.Column('rr_thresh_high', db.Float, unique=False)
    temp_thresh_high = db.Column('temp_thresh_high', db.Float, unique=False)
    hr_thresh_low = db.Column('hr_thresh_low', db.Float, unique=False)
    rr_thresh_low = db.Column('rr_thresh_low', db.Float, unique=False)
    temp_thresh_low = db.Column('temp_thresh_low', db.Float, unique=False)
    alarm_state = db.Column('alarm_state', db.Boolean, unique=False)

''' Done Defining Database Objects '''

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
	# these are dummy variables
	id = 3
	ms = 24000000 # this is about 6.67 hours
	our_time = 73.0
	now = datetime.datetime.now()
	then = now - datetime.timedelta(hours=0, minutes=ms/60000)
	hr = 58.3
	rr = 12.3
	temp = 37.2

	datapts = 72 # once an hour for three days

	# in a loop
	while True:
		query = Vital.query.filter(Vital.id==id)
		add_vital = Vital(id=id, time=our_time, datetime=then, hr=hr, rr=rr, temp=temp)
		db.session.add(add_vital)
		if query.count() > datapts:
			db.session.delete(query.first())
		db.session.commit()
		time.sleep(1)
	# end of loop




	# after loop
	db.session.commit()








if __name__ == "__main__":
	main()

