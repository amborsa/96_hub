# importing Python package dependencies
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
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

    ''' this just edits alarm states in input.db -->
    this will eventually need to be replaced by the script that
    actually analyzes data from vitals.db and gives an alarm-state
    output '''
    guess = random.randint(1,20)
    row = Input.query.filter(Input.id==guess).first()
    if row.alarm_state==True:
        row.alarm_state = False
    else:
        row.alarm_state = True
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
        return render_template("input.html", id=id)

@app.route('/patient/<id>', methods=["GET"])
def patient(id):
    # In this function, we need to get an list of dictionaries that has the data
    # # ex: temp = [{t:98},{t:99}, ...]
    temp = db.execute("SELECT temp,time FROM Vital WHERE id = :id", id = id)
    HeartRate = db.execute("SELECT hr,time FROM Vital WHERE id = :id", id = id)
    RR = db.execute("SELECT rr,time FROM Vital WHERE id = :id", id = id)
    # Make sure it works for just one case first
    # :id", id = id
    # RR_list = []
    # for i in range(len(RR)):
    #     RR_value = RR[i]
    #     RR_list.append(RR_value)
    # Put this following comment into render.template
    # , Temperature=temp_list,HeartRate=hr_list, RespiratoryRate=RR_list
    return render_template("patient.html", id=id, Temperature=temp_list,HeartRate=hr_list, RespiratoryRate=RR_list)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
