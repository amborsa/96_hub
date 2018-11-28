# importing Python package dependencies
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify,json,Markup
from flask_sqlalchemy import SQLAlchemy
from tempfile import gettempdir
import random
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
    time = db.Column('time', db.Float, unique=False)
    hr = db.Column('hr', db.Float, unique=False)
    rr = db.Column('rr', db.Float, unique=False)
    temp = db.Column('temp', db.Float, unique=False)

# fields: device id (unique), name, hr threshold, rr threshold, temp threshold, alarm state
class Input(db.Model):
    __bind_key__ = "inputs"
    id = db.Column('id', db.Integer, primary_key=True)
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
    ids = []
    names = []
    alarm_states = []
    full_query = Input.query.all()
    for query in full_query:
        ids.append(query.id)
        names.append(query.name)
        alarm_states.append(query.alarm_state)
    devices = []
    for i in range(len(ids)):
        new_dict = {'id': ids[i], 'name': names[i], 'alarm_state': \
            alarm_states[i]}
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

        # analyzing the vitals to determine alarm state


        # if max(hrs[-5:]) >= hr_high or min(hrs[-5:]) <= hr_low or max(rrs[-5:]) >= rr_high or min(rrs[-5:]) <= rr_low or \
        # max(temps[-5:]) >= temp_high or min(temps[-5:]) <= temp_low:
        #     alarm_state = True
        # else:
        #     alarm_state = False

        age = input_query_id.age

        vthresh(hrs[-1], rrs[-1], temps[-1])
        
        # commit to database
        input_query_id.alarm_state = alarm_state
        db.session.commit()


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

    return jsonify(devices)


@app.route('/input/<id>', methods=["GET", "POST"])
def input(id):
    if request.method == "GET":

        input_query_id = Input.query.filter(Input.id==id).first()

        # for each ID, acquire HR, RR, and temp thresholds
        age = input_query_id.age
        hr_low = input_query_id.hr_thresh_low
        hr_high = input_query_id.hr_thresh_high
        rr_low = input_query_id.rr_thresh_low
        rr_high = input_query_id.rr_thresh_high
        temp_low = input_query_id.temp_thresh_low
        temp_high = input_query_id.temp_thresh_high
        name = input_query_id.name
        return render_template("input.html", id=id, name=name, hr_low=hr_low, hr_high=hr_high, rr_low=rr_low, \
            rr_high=rr_high, temp_low=temp_low, temp_high=temp_high, age=age)

    if request.method == "POST":

        # populate database with form data
        if request.form['btn_identifier']=="set":
            input_query_id = Input.query.filter(Input.id==id).first()
            input_query_id.name = request.form['inputName']
            input_query_id.age = request.form['inputAge']
            input_query_id.rr_thresh_low = request.form['inputRRlower']
            input_query_id.rr_thresh_high = request.form['inputRRupper']
            input_query_id.hr_thresh_low = request.form['inputHRlower']
            input_query_id.hr_thresh_high = request.form['inputHRupper']
            input_query_id.temp_thresh_low = request.form['inputTemplower']
            input_query_id.temp_thresh_high = request.form['inputTempupper']
            db.session.commit()

        # populate database with "standard values" -- these values should be researched and updated
        elif request.form['btn_identifier']=="reset":
            input_query_id = Input.query.filter(Input.id==id).first()
            input_query_id.name = ""
            input_query_id.age = ""
            input_query_id.rr_thresh_low = 20.0
            input_query_id.rr_thresh_high = 50.0
            input_query_id.hr_thresh_low = 45.0
            input_query_id.hr_thresh_high = 110.0
            input_query_id.temp_thresh_low = 35.0
            input_query_id.temp_thresh_high = 38.5
            db.session.commit()

<<<<<<< HEAD
            # age = input_query_id.age
            # hr_low = input_query_id.hr_thresh_low
            # hr_high = input_query_id.hr_thresh_high
            # rr_low = input_query_id.rr_thresh_low
            # rr_high = input_query_id.rr_thresh_high
            # temp_low = input_query_id.temp_thresh_low
            # temp_high = input_query_id.temp_thresh_high
            # name = input_query_id.name

            # def vthresh(age, hr_low, hr_high, rr_low, rr_high, temp_low, temp_high)
            #     if temp_low < 100
            #     if temp_low <101
            #     if temp_low <102
            #     if temp_low < 103
            #     if temp_low < 104
            #     if temp_low < 105
            #     if temp_ high > 105





=======
>>>>>>> 729bbeca7378c8bfec40bf9ce602a782530baee5

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
