''' GENERAL NOTES '''
''' check for tab issues with python -m tabnanny yourfile.py '''

from flask import Flask, flash, redirect, render_template, request, session, url_for
from tempfile import gettempdir

app = Flask(__name__)

# caches should not be stored
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

@app.route('/')
def main():
    """Show main page"""

    # this array should be selected from the database
    ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 19]
    names=["John", "Jim", "Jade", "John", "Jim", "Jade", "John", "Jim", "Jade", "John", "Jim", "Jade", "John", "Jim", "Jade", \
    "John"]
    devices = []
    for i in range(len(ids)):
        new_dict = {'id': ids[i], 'name': names[i]}
        devices.append(new_dict)

    return render_template("main.html", devices=devices)

@app.route('/input/<id>', methods=["GET", "POST"])
def input(id):
    if request.method == "GET":
        return render_template("input.html", id=id)

@app.route('/patient/<id>', methods=["GET"])
def patient(id):
    return render_template("patient.html", id=id)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


