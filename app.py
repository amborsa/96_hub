# importing Python package dependencies
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify,json,Markup
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
        if max(hrs[-5:]) >= hr_high or min(hrs[-5:]) <= hr_low or max(rrs[-5:]) >= rr_high or min(rrs[-5:]) <= rr_low or \
        max(temps[-5:]) >= temp_high or min(temps[-5:]) <= temp_low:
            alarm_state = True
        else:
            alarm_state = False

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
        hr_low = input_query_id.hr_thresh_low
        hr_high = input_query_id.hr_thresh_high
        rr_low = input_query_id.rr_thresh_low
        rr_high = input_query_id.rr_thresh_high
        temp_low = input_query_id.temp_thresh_low
        temp_high = input_query_id.temp_thresh_high
        name = input_query_id.name
        return render_template("input.html", id=id, name=name, hr_low=hr_low, hr_high=hr_high, rr_low=rr_low, \
            rr_high=rr_high, temp_low=temp_low, temp_high=temp_high)

    if request.method == "POST":

        # populate database with form data
        if request.form['btn_identifier']=="set":
            input_query_id = Input.query.filter(Input.id==id).first()
            input_query_id.name = request.form['inputName']
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
            input_query_id.rr_thresh_low = 20.0
            input_query_id.rr_thresh_high = 50.0
            input_query_id.hr_thresh_low = 45.0
            input_query_id.hr_thresh_high = 110.0
            input_query_id.temp_thresh_low = 35.0
            input_query_id.temp_thresh_high = 38.5
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

    # NUMBER.columnname will access a cell in the table
    for query in full_query:
        hr.append(query.hr)
        temp.append(query.temp)
        rr.append(query.rr)
        time.append(query.time)
    return render_template("patient.html",id=id, title1="Heart Rate",title2="Temperature",title3="Respiratory Rate",\
        values1 = hr, labels = time, max1 = 250, values2 = temp, max2 = 50, values3 = rr, max3 = 50)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
