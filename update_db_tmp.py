'''This is not a file for the final web application.'''
'''The purpose of this file is to randomly change alarm states.'''

# importing Python package dependencies
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from tempfile import gettempdir
import random
import time

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

# making continuous and random changes to database:input
while True:
    time.sleep(random.randint(1,10))
    guess = random.randint(1,20)
    print(guess)
    row = Input.query.filter(Input.id==guess).first()
    if row.alarm_state==True:
        row.alarm_state = False
    else:
        row.alarm_state = True
    db.session.commit()