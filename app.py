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

global num_vitals
num_vitals = 72


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
        dob = query.dob
        str_dob = dob.strftime('%m-%d-%Y')
        dobs.append(str_dob)
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
    # catching zmq.error.Again and other errors
    except:
        # did not receive string from client
        socket.close()
        context.term()
        return ("", 204)

    ## add vital data row into database
    ## drop row, if necessary

    serial = q.get()
    serial_parsed = serial.split(",")
    node = int(serial_parsed[0])
    minute_delay = float(serial_parsed[1])/60000
    hr = float(serial_parsed[2])
    rr = float(serial_parsed[3])
    temp = float(serial_parsed[4])
    now = datetime.datetime.now()
    timestamp = now - datetime.timedelta(minutes=minute_delay)

    input_query = Input.query.filter(Input.node==node).first()
    patient_id = input_query.id

    age = calculate_age_months(input_query.dob, now)

    add_vital = Vital(id=patient_id, time=0, datetime=timestamp, hr=hr, rr=rr, temp=temp)
    db.session.add(add_vital)

    vital_query = Vital.query.filter(Vital.id==patient_id).order_by(Vital.e_id) # first index is earliest vital
    if vital_query.count() >= 72:
        db.session.delete(vital_query.first())

    hr_low = input_query.hr_thresh_low
    hr_high = input_query.hr_thresh_high
    rr_low = input_query.rr_thresh_low
    rr_high = input_query.rr_thresh_high
    temp_low = input_query.temp_thresh_low
    temp_high = input_query.temp_thresh_high

    if hr >= hr_high or hr <= hr_low or rr >= rr_high or rr <= rr_low or \
    temp >= temp_high or temp <= temp_low:
        alarm_state = True
    else:
        alarm_state = False

    if input_query.alarm_state is not alarm_state:
        input_query.alarm_state = alarm_state

    db.session.commit()

    to_serial = str(age) + "," + str(int(alarm_state))

    socket.send_string(to_serial)
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
        age_year = int(datetime.datetime.today().strftime('%Y')) - int(dob.strftime('%Y'))
        age_month = int(datetime.datetime.today().strftime('%m')) - int(dob.strftime('%m'))
        age_day = int(datetime.datetime.today().strftime('%d')) - int(dob.strftime('%d'))

        # calculate age
        age = age_year + age_month/12 + age_day/365

        return render_template("input.html", id=id, name=name, hr_low=hr_low, hr_high=hr_high, rr_low=rr_low,
            rr_high=rr_high, temp_low=temp_low, temp_high=temp_high, current_date = current_date,
            dob=dob.strftime('%Y-%m-%d'), loc=loc, age=age)

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

            # dob = datetime.strptime(strdob, '%Y-%m-%d')
            loc = request.form['inputloc']

            # updating changed fields in input database
            input_query_id = Input.query.filter(Input.id==id).first()
            if input_query_id.name is not request.form['inputName']:
                input_query_id.name = request.form['inputName']
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
            if input_query_id.dob is not datetime.datetime.strptime(dob, '%Y-%m-%d'):
                input_query_id.dob = datetime.datetime.strptime(dob, '%Y-%m-%d')
            if input_query_id.loc is not loc:
                input_query_id.loc = loc

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
    temp_all = []
    hr_all = []
    rr_all = []
    datetime_all = []
    date_all = []
    time_daily = []
    time_longitudinal = []
    index_list = []
    # Acesses the entire table, each row is an Objects
    # ex: full_query(0) = the title of categories row

    full_query = Vital.query.filter(Vital.id==id)
    full_query_thresholds = Input.query.filter(Input.id==id)

    # NUMBER.columnname will access a cell in the table
    for query in full_query:
        hr_all.append(query.hr)
        temp_all.append(query.temp)
        rr_all.append(query.rr)
        datetime_all.append(query.datetime)

    # Get current date and time (year-month-day) (hour-minute-second-microsecond)
    # https://stackoverflow.com/questions/415511/how-to-get-the-current-time-in-python
    datenow = datetime.datetime.now()
    datenow = datetime.date(datenow.year, datenow.month, datenow.day)
    timenow = datetime.datetime.now().time()

    # Get only the date for time stamps for longitudinal graphs (only year, month, day)
    for i in range(len(datetime_all)):
        date_all.append(datetime.date(datetime_all[i].year, datetime_all[i].month, datetime_all[i].day))

    # Get only the last day's worth of data for the first graph
    # https://stackoverflow.com/questions/415511/how-to-get-the-current-time-in-python
    for index in range(len(date_all)):
        difference = datenow - date_all[index]
        if difference.days == 0:
            time_daily.append(datetime_all[index].strftime('%H:%M:%S'))
            index_list.append(index)


    # Get the vital data from the last day for first graph
    hr_graph1 = []
    rr_graph1 = []
    temp_graph1 = []
    for i in range(len(index_list)):
        hr_graph1.append(hr_all[index_list[i]])
        rr_graph1.append(rr_all[index_list[i]])
        temp_graph1.append(temp_all[index_list[i]])

    # Now get the mean value for the last 5 days in the past
    days_ago = 5
    # Start by getting a list of each day
    hr_long = []
    rr_long = []
    temp_long = []
    # Set these lists to store the mean values
    hr_graph2 = []
    rr_graph2 = []
    temp_graph2 = []
    time_graph2 = []
    for i in range(days_ago):
        # Go through each previous day
        past_date = datenow - datetime.timedelta(days=(days_ago-i))
        # Get the index for data on that day
        for index in range(len(date_all)):
            difference = past_date - date_all[index]
            if difference.days == 0:
                index_list.append(index)
        # Make a list of vital data for that day
        for i in range(len(index_list)):
            hr_long.append(hr_all[index_list[i]])
            rr_long.append(rr_all[index_list[i]])
            temp_long.append(temp_all[index_list[i]])
        # Find the mean of each vital for that day
        hr_mean = sum(hr_long)/len(hr_long)
        rr_mean = sum(rr_long)/len(rr_long)
        temp_mean = sum(temp_long)/len(temp_long)
        # Store the mean value into a the 2nd graph data list
        hr_graph2.append(hr_mean)
        rr_graph2.append(rr_mean)
        temp_graph2.append(temp_mean)
        time_graph2.append(past_date)

    # Make a repeated list of the thresholds for the plotted line
    hr_high = []
    hr_low = []
    rr_high = []
    rr_low = []
    temp_high = []
    temp_low = []
    name = []
    dob = []
    for query2 in full_query_thresholds:
        name.append(query2.name)
        dob.append(query2.dob)
    name = name[0]
    dob = dob[0]
    dob = datetime.date(dob.year, dob.month, dob.day)

    # Calculate patient's age for standardized thresholds
    age_months = calculate_age_months(dob,datenow)
    age = age_months/12
    standard_thresholds = vitalthresh(age)

    # return(upperRR, lowerRR, upperHR, lowerHR, upperTemp, lowerTemp)
    rr_high.append(standard_thresholds[0])
    rr_low.append(standard_thresholds[1])
    hr_high.append(standard_thresholds[2])
    hr_low.append(standard_thresholds[3])
    temp_high.append(standard_thresholds[4])
    temp_low.append(standard_thresholds[5])

    # Make these values a list for the graph
    hr_high = hr_high*len(index_list)
    hr_low = hr_low*len(index_list)
    rr_high = rr_high*len(index_list)
    rr_low = rr_low*len(index_list)
    temp_high = temp_high*len(index_list)
    temp_low = temp_low*len(index_list)

    # Set max and min values for graph axes ranges
    # If the threshold value is less than the lowest data point, then use the threshold value as the lower axis
    hr_max = max(hr_all)
    hr_min = min(hr_all)
    rr_max = max(rr_all)
    rr_min = min(rr_all)
    temp_max = max(temp_all)
    temp_min = min(temp_all)
    # Compare hr min and maxes to threshold values
    # hr_upper
    if hr_max > hr_high[0]:
        hr_upper = hr_max + 10
    else:
        hr_upper = hr_high[0] + 10
    # hr_lower
    if hr_min < hr_low[0]:
        hr_lower = hr_min - 10
    else:
        hr_lower = hr_low[0] - 10
    # Do the same for respiratory rate
    # rr_upper
    if rr_max > rr_high[0]:
        rr_upper = rr_max + 1
    else:
        rr_upper = rr_high[0] + 1
    # rr_lower
    if rr_min < rr_low[0]:
        rr_lower = rr_min - 1
    else:
        rr_lower = rr_low[0] - 1
    # Do the same for temperature
    # temp_upper
    if temp_max > temp_high[0]:
        temp_upper = temp_max + 1
    else:
        temp_upper = temp_high[0] + 1
    # temp_lower
    if temp_min < temp_low[0]:
        temp_lower = temp_min - 1
    else:
        temp_lower = temp_low[0] - 1
    hr_range = round(hr_max) - round(hr_min)
    temp_range = round(temp_max) - round(temp_min)
    rr_range = round(rr_max) - round(rr_min)

    # Create axes ranges for longitudinal graphs
    if min(hr_graph2) == 0:
        hr_min_long = hr_lower
        rr_min_long = rr_lower
        temp_min_long = temp_lower
    else:
        hr_min_long = min(hr_graph2) - 1
        rr_min_long = min(rr_graph2) - 1
        temp_min_long = min(temp_graph2) - 1


    # Send all values to html file to graph
    return render_template("patient.html",id=name, title1="Heart Rate",title2="Temperature",title3="Respiratory Rate", labels1 = time_daily,labels2 = time_graph2, values1day = hr_graph1,values1long = hr_graph2, max1 = hr_upper, min1 = hr_lower, range1 = hr_range, high1 = hr_high, low1 = hr_low, min1long = hr_min_long, values2day = temp_graph1,values2long = temp_graph2, max2 = temp_upper, min2 = temp_lower, range2 = temp_range, high2 = temp_high, low2 = temp_low,min2long = temp_min_long, values3day = rr_graph1,values3long = rr_graph2, max3 = rr_upper, min3 = rr_lower, range3 = rr_range, high3 = rr_high, low3 = rr_low,min3long = rr_min_long,)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
