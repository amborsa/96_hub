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
    ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19]

	return render_template("main.html", ids=ids)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


