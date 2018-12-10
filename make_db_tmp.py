'''This is not a file for the final web application.'''
'''The purpose of this file is to populate the databases with dummy values.'''
'''This should not be run if there are pre-existing, populated databases.'''

# importing Python package dependencies
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from tempfile import gettempdir
import random
import datetime
from helpers import *

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
    surname = db.Column('surname', db.String(30), unique=False)
    loc = db.Column('loc', db.String(30), unique=False)
    dob = db.Column('dob', db.DateTime, unique=False)
    med_id = db.Column('med_id', db.String(15), unique=False)
    diagnosis = db.Column('diagnosis', db.String(30), unique=False)
    hr_thresh_high = db.Column('hr_thresh_high', db.Float, unique=False)
    rr_thresh_high = db.Column('rr_thresh_high', db.Float, unique=False)
    temp_thresh_high = db.Column('temp_thresh_high', db.Float, unique=False)
    hr_thresh_low = db.Column('hr_thresh_low', db.Float, unique=False)
    rr_thresh_low = db.Column('rr_thresh_low', db.Float, unique=False)
    temp_thresh_low = db.Column('temp_thresh_low', db.Float, unique=False)
    # 0=no alarm, 1=alarm, 2=near alarm state
    alarm_state = db.Column('alarm_state', db.Integer, unique=False)

''' Done Defining Database Objects '''

# this makes the databases (assuming there are no databases to start with)
db.create_all()

# this adds test data to the input database
ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
nodes = [2, 4, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
names = ["John", "Jane", "John", "Jane", "John", "Jane", "John", "Jane", "John", "Jane", "John", "Jane", \
"John", "Jane", "John", "Jane", "John", "Jane", "John", "Jane"]
surnames = []
med_ids = []
diagnosis = []
locs = []
dobs = []
hr_threshes_high = []
rr_threshes_high = []
temp_threshes_high = []
hr_threshes_low = []
rr_threshes_low = []
temp_threshes_low = []
alarm_states = []
for i in range(20):
    locs.append("B" + str(i+1))
    dob = datetime.datetime(random.randint(2008, 2015), random.randint(1,12), random.randint(1,28), \
        hour=0, minute=0, second=0, microsecond=0)
    now = datetime.datetime.now()
    age_months = calculate_age_months(dob, now)
    age = age_months/12
    rr_high, rr_low, hr_high, hr_low, temp_high, temp_low = vitalthresh(age)
    dobs.append(dob)
    surnames.append("Doe")
    med_ids.append(random.randint(1000, 9999))
    diagnosis.append("ALL")
    alarm_states.append(0)
    hr_threshes_high.append(hr_high)
    rr_threshes_high.append(rr_high)
    temp_threshes_high.append(temp_high)
    hr_threshes_low.append(hr_low)
    rr_threshes_low.append(rr_low)
    temp_threshes_low.append(temp_low)

for i in range(len(ids)):
    add_input = Input(id=ids[i], name=names[i], hr_thresh_high=hr_threshes_high[i], rr_thresh_high=rr_threshes_high[i], \
        temp_thresh_high=temp_threshes_high[i], hr_thresh_low=hr_threshes_low[i], rr_thresh_low=rr_threshes_low[i], \
        temp_thresh_low=temp_threshes_low[i], alarm_state=alarm_states[i], dob=dobs[i], loc=locs[i], node=nodes[i], \
        surname=surnames[i], med_id=med_ids[i], diagnosis=diagnosis[i])
    db.session.add(add_input)
db.session.commit()

# this adds test data to the vitals database
ids = ids
times = []
datetimes = []
for i in range(72):
    datetimes.append(datetime.datetime.now()+datetime.timedelta(hours=(i-72), minutes=0))
e_id_ticker = 0
for i in range(len(datetimes)):
	for n_id in ids:
		hr = random.uniform(70.0, 75.0)
		rr = random.uniform(10.0, 12.0)
		temp = random.uniform(36.5, 37.0)
		add_vital = Vital(e_id=e_id_ticker, id=n_id, datetime=datetimes[i], hr=hr, rr=rr, temp=temp)
		db.session.add(add_vital)
		e_id_ticker += 1
db.session.commit()