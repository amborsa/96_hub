from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)

@app.route('/')
def index():
    # vitals = db.execute("SELECT * FROM Patient1 WHERE time = (SELECT MAX(time) FROM Patient1)")
    # hr = vitals[0]["hr"]
    # temp = vitals[0]["temp"]
    # rr = vitals[0]["rr"]
    # current_vital = [hr, temp, rr]
    # ,vital = current_vital
    return render_template("main.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
