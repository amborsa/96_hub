# importing Python package dependencies
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify, json, Markup
from flask_sqlalchemy import SQLAlchemy
from tempfile import gettempdir
import random
from helpers import *
import datetime as datetime
import threading
import zmq
import queue
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



@app.route('/')
def main():
    """Show main page"""

    ''' grabs and organizes database:input data --> let's make this a function later '''
    ids = ["Device ID"]
    names = ["Name"]
    alarm_states = [0]
    locs = ["Location"]
    dobs = ["Birth Date"]
    full_query = Input.query.all()
    for query in full_query:
        ids.append(query.id)
        names.append(query.name)
        locs.append(query.loc)
        dobs.append(query.dob)
        alarm_states.append(query.alarm_state)
    devices = []
    for i in range(len(ids)):
        new_dict = {'id': ids[i], 'name': names[i], 'alarm_state': \
            alarm_states[i], 'loc': locs[i], 'dob': dobs[i]}
        devices.append(new_dict)
    ''' done grabbing and organizing database:input data '''

    return render_template("main.html", devices=devices)

@app.route('/update_main', methods=["POST"])
def update_main():    

    input_query_all = Input.query.all()

    ids = []
    for query in input_query_all:
        ids.append(query.id)

    for id in ids:
        # id specific queries
        vital_query = Vital.query.filter(Vital.id==id).order_by(Vital.time)
        input_query_id = Input.query.filter(Input.id==id).first()

        # thresholds
        hr_low = input_query_id.hr_thresh_low
        hr_high = input_query_id.hr_thresh_high
        rr_low = input_query_id.rr_thresh_low
        rr_high = input_query_id.rr_thresh_high
        temp_low = input_query_id.temp_thresh_low
        temp_high = input_query_id.temp_thresh_high

        # vitals and time into arrays
        hrs = []
        rrs = []
        temps = []
        time = []
        for row in vital_query:
            hrs.append(row.hr)
            rrs.append(row.rr)
            temps.append(row.temp)
            time.append(row.time)


    ''' grabs and organizes input.db data '''
    ids = []
    alarm_states = []
    full_query = Input.query.all()
    for query in full_query:
        ids.append(query.id)
        alarm_states.append(query.alarm_state)
    devices = []
    for i in range(len(ids)):
        new_dict = {'id': ids[i], 'alarm_state': \
            alarm_states[i]}
        devices.append(new_dict)
    ''' done grabbing and organizing database:input data '''

    # sending alarm states to serialreader
    # socket.send_string(' '.join(str(int(e)) for e in alarm_states))

    return jsonify(devices)

@app.route('/serial_listen', methods=["POST"])
def serial_listen():

    q = queue.Queue(maxsize=0)
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.setsockopt(zmq.RCVTIMEO, 1000);
    print("Collecting key polling data from the server")
    socket.bind("tcp://*:5556")

    try:
        com_string = socket.recv_string()
        q.put(com_string)
        print(q.get())
    except zmq.error.Again:
        # did not receive string from client
        return ("", 204)

    # selecting data
    input_query_all = Input.query.all()

    ids = []
    for query in input_query_all:
        ids.append(query.id)

    alarm_states = []
    for id in ids:
        # id specific queries
        vital_query = Vital.query.filter(Vital.id==id).order_by(Vital.e_id.desc()).first()
        input_query_id = Input.query.filter(Input.id==id).first()

        # thresholds
        hr_low = input_query_id.hr_thresh_low
        hr_high = input_query_id.hr_thresh_high
        rr_low = input_query_id.rr_thresh_low
        rr_high = input_query_id.rr_thresh_high
        temp_low = input_query_id.temp_thresh_low
        temp_high = input_query_id.temp_thresh_high

        # vals
        hr = vital_query.hr
        rr = vital_query.rr
        temp = vital_query.temp

        # vitals and time into arrays
        if hr >= hr_high or hr <= hr_low or rr >= rr_high or rr <= rr_low or \
        temp >= temp_high or temp <= temp_low:
            alarm_state = True
        else:
            alarm_state = False
        
        alarm_states.append(alarm_state)
        # commit alarm state to database
        if input_query_id.alarm_state is not alarm_state:
            input_query_id.alarm_state = alarm_state
    
    db.session.commit()
    socket.send_string(' '.join(str(int(e)) for e in alarm_states))
    # socket.send_string("success")
    socket.close()
    context.term()

    return ("", 204)


@app.route('/input/<id>', methods=["GET", "POST"])
def input(id):
    if request.method == "GET":

        input_query_id = Input.query.filter(Input.id==id).first()

        # for each ID, acquire HR, RR, and temp thresholds
        # age = input_query_id.age
        hr_low = input_query_id.hr_thresh_low
        hr_high = input_query_id.hr_thresh_high
        rr_low = input_query_id.rr_thresh_low
        rr_high = input_query_id.rr_thresh_high
        temp_low = input_query_id.temp_thresh_low
        temp_high = input_query_id.temp_thresh_high
        name = input_query_id.name

        dob = input_query_id.dob
        loc = input_query_id.loc

        # current date

        current_date = datetime.datetime.today().strftime('%Y-%m-%d')

        # difference between birthdate (year, month, day) to current date
        age_year = int(datetime.datetime.today().strftime('%Y')) - int(dob[0:4])
        age_month = int(datetime.datetime.today().strftime('%m')) - int(dob[5:7])
        age_day = int(datetime.datetime.today().strftime('%d')) - int(dob[8:10])

        # calculate age 
        age = age_year + age_month/12 + age_day/365

        return render_template("input.html", id=id, name=name, hr_low=hr_low, hr_high=hr_high, rr_low=rr_low, 
            rr_high=rr_high, temp_low=temp_low, temp_high=temp_high, age_year=age_year, age_month=age_month, 
            age_day=age_day, current_date = current_date, dob=dob, loc=loc, age=age)

    if request.method == "POST":

        # populate database with form data
        if request.form['btn_identifier']=="set":
            # querying vitals to immediately update alarm state
            vital_query = Vital.query.filter(Vital.id==id).order_by(Vital.e_id.desc()).first()
            hr = vital_query.hr
            rr = vital_query.rr
            temp = vital_query.temp

            hr_high = float(request.form['inputHRupper'])
            hr_low = float(request.form['inputHRlower'])
            rr_high = float(request.form['inputRRupper'])
            rr_low = float(request.form['inputRRlower'])
            temp_high = float(request.form['inputTempupper'])
            temp_low = float(request.form['inputTemplower'])
            dob = request.form['inputDOB']
            loc = request.form['inputloc']

            # updating changed fields in input database
            input_query_id = Input.query.filter(Input.id==id).first()
            if input_query_id.name is not request.form['inputName']:
                input_query_id.name = request.form['inputName']
            # input_query_id.age = request.form['inputAge']
            if input_query_id.rr_thresh_low is not rr_low:
                input_query_id.rr_thresh_low = rr_low
            if input_query_id.rr_thresh_high is not rr_high:
                input_query_id.rr_thresh_high = rr_high
            if input_query_id.hr_thresh_low is not hr_low:
                input_query_id.hr_thresh_low = hr_low
            if input_query_id.hr_thresh_high is not hr_high:
                input_query_id.hr_thresh_high = hr_high
            if input_query_id.temp_thresh_low is not temp_low:
                input_query_id.temp_thresh_low = temp_low
            if input_query_id.temp_thresh_high is not temp_high:
                input_query_id.temp_thresh_high = temp_high
            if input_query_id.dob is not dob:
                input_query_id.dob = dob
            if input_query_id.loc is not loc:
                input_query_id.loc = loc

            # calculating and updating alarm state
            if hr >= hr_high or hr <= hr_low or rr >= rr_high or rr <= rr_low or \
            temp >= temp_high or temp <= temp_low:
                alarm_state = True
            else:
                alarm_state = False
            if input_query_id.alarm_state is not alarm_state:
                input_query_id.alarm_state = alarm_state
            db.session.commit()

        # populate database with "standard values" -- these values should be researched and updated
        elif request.form['btn_identifier']=="reset":
            input_query_id = Input.query.filter(Input.id==id).first()
            input_query_id.name = ""
            # input_query_id.age = ""
            input_query_id.rr_thresh_low = 20.0
            input_query_id.rr_thresh_high = 50.0
            input_query_id.hr_thresh_low = 45.0
            input_query_id.hr_thresh_high = 110.0
            input_query_id.temp_thresh_low = 35.0
            input_query_id.temp_thresh_high = 38.5
            input_query_id.dob = ""
            input_query_id.loc = ""
            db.session.commit()


        return redirect(url_for("main"))

@app.route('/patient/<id>', methods=["GET"])
def patient(id):
    # In this function, we need to get an list of dictionaries that has the data
    # # ex: temp = [{t:98},{t:99}, ...]
    temp = []
    hr = []
    rr = []
    time = []
    # Acesses the entire table, each row is an Objects
    # ex: full_query(0) = the title of categories row

    full_query = Vital.query.filter(Vital.id==id)
    full_query_thresholds = Input.query.filter(Input.id==id)

    # NUMBER.columnname will access a cell in the table
    for query in full_query:
        hr.append(query.hr)
        temp.append(query.temp)
        rr.append(query.rr)
        time.append(query.time)

    # Make a repeated list of the thresholds for the plotted line
    hr_high = []
    hr_low = []
    rr_high = []
    rr_low = []
    temp_high = []
    temp_low = []
    for query2 in full_query_thresholds:
        hr_high.append(query2.hr_thresh_high)
        hr_low.append(query2.hr_thresh_low)
        rr_high.append(query2.rr_thresh_high)
        rr_low.append(query2.rr_thresh_low)
        temp_high.append(query2.temp_thresh_high)
        temp_low.append(query2.temp_thresh_low)
    hr_high = hr_high*len(hr)
    hr_low = hr_low*len(hr)
    rr_high = rr_high*len(rr)
    rr_low = rr_low*len(rr)
    temp_high = temp_high*len(temp)
    temp_low = temp_low*len(temp)

    # Set max and min values for graph axes ranges
    hr_max = max(hr) + 5
    hr_min = min(hr) - 5
    rr_max = max(rr) + 5
    rr_min = min(rr) - 5
    temp_max = max(temp) + 1
    temp_min = min(temp) - 1
    hr_range = round(hr_max) - round(hr_min)
    temp_range = round(temp_max) - round(temp_min)
    rr_range = round(rr_max) - round(rr_min)
    # print(hr_high)
    # print(hr)
    return render_template("patient.html",id=id, title1="Heart Rate",title2="Temperature",title3="Respiratory Rate", labels = time, values1 = hr, max1 = hr_max, min1 = hr_min, range1 = hr_range, high1 = hr_high, low1 = hr_low, values2 = temp, max2 = temp_max, min2 = temp_min, range2 = temp_range, values3 = rr, max3 = rr_max, min3 = rr_min, range3 = rr_range)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
