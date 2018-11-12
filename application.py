from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from datetime import datetime
from pytz import timezone

# Import math python libraries
import numpy as np
import matplotlib.pyplot as plt
    # N = 8
    # x = np.linspace(0,100,N)
    # plt.plot(x, 2*x, 'o')

from helpers import login_required, apology

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///vitals.db")

@app.route("/")
def index():
    vitals = db.execute("SELECT * FROM Patient1 WHERE time = (SELECT MAX(time) FROM Patient1)")
    hr = vitals[0]["hr"]
    temp = vitals[0]["temp"]
    rr = vitals[0]["rr"]
    current_vital = [hr, temp, rr]
    return render_template("index.html", vital = current_vital)

@app.route("/patientgraphs")
def patientgraphs():
    return render_template("patientgraphs.html")
    ## These lines make an array of vital data
    # temperature_list_dict = db.execute("SELECT temp FROM Patient1 WHERE id = :id", id = id)
    # temperature_array = []
    # for i in range(len(temperature_list_dict)):
    #     temp_value = temperature_list_dict[i]["temp"]
    #     temperature_array.append(temp_value)
    # return render_template("patientgraphs.html",temp = temperature_array)

@app.route("/patientselect", methods=["GET","POST"])
def patientselect():
    if request.method == "GET":
        ids = db.execute("SELECT DISTINCT id FROM Patient1")
        ids_list = []
        for i in range(len(ids)):
            patient_id = ids[i]["id"]
            ids_list.append(patient_id)
        return render_template("patientselect.html", ids_list = ids_list)
    if request.method == "POST":
        return render_template("patientgraphs.html")
