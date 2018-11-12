from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("main.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
