'''This is not a file for the final web application.'''
'''The purpose of this file is to randomly change alarm states.'''

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
'''Done Initializing App and Database '''


''' Defining Database Objects '''
# fields: entry id (unique), device id, time, hr, rr, temp
# NOTE: there is also a date datatype (potentially for time)
class Vital(db.Model):
    __bind_key__ = "vitals"
    e_id = db.Column('e_id', db.Integer, primary_key=True)
    id = db.Column('id', db.Integer, unique=False)
    time = db.Column('time', db.Float, unique=False)
    hr = db.Column('hr', db.Float, unique=False)
    rr = db.Column('rr', db.Float, unique=False)
    temp = db.Column('temp', db.Float, unique=False)

# fields: device id (unique), name, hr threshold, rr threshold, temp threshold, alarm state
class Input(db.Model):
    __bind_key__ = "inputs"
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(30), unique=False)
    hr_thresh = db.Column('hr_thresh', db.Float, unique=False)
    rr_thresh = db.Column('rr_thresh', db.Float, unique=False)
    temp_thresh = db.Column('temp_thresh', db.Float, unique=False)
    alarm_state = db.Column('alarm_state', db.Boolean, unique=False)
''' Done Defining Database Objects '''

# this makes the databases (assuming there are no databases to start with)
db.create_all()

# this adds test data to the input database
ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
names = ["Daniel", "Anisha", "Allegra", "Adriano", "Michelle", "Simone", "Jesse", "Tatheer", "Olivia", "Jazmin", "Jason", \
"Andrew", "Joel", "Nic", "Aileen", "Cathy", "Awnit", "Colin", "Anisha", "Nathan"]
hr_threshes = []
rr_threshes = []
temp_threshes = []
alarm_states = []
for i in range(20):
	hr_threshes.append(random.uniform(100.0, 150.0))
	rr_threshes.append(random.uniform(20.0, 40.0))
	temp_threshes.append(random.uniform(37.0, 40.0))
	if random.randint(0,1)==0:
		alarm_states.append(True)
	else:
		alarm_states.append(False)

for i in range(len(ids)):
	add_input = Input(id=ids[i], name=names[i], hr_thresh=hr_threshes[i], rr_thresh=rr_threshes[i], \
		temp_thresh=temp_threshes[i], alarm_state=alarm_states[i])
	db.session.add(add_input)
db.session.commit()

# this adds test data to the vitals database
ids = ids
times = []
ticker = 0.0
for i in range(48):
	times.append(ticker)
	ticker += 10.0
e_id_ticker = 0
for time in times:
	for n_id in ids:
		hr = random.uniform(50.0, 150.0)
		rr = random.uniform(8.0, 30.0)
		temp = random.uniform(34.0, 39.0)
		add_vital = Vital(e_id=e_id_ticker, id=n_id, time=time, hr=hr, rr=rr, temp=temp)
		db.session.add(add_vital)
		e_id_ticker += 1
db.session.commit()