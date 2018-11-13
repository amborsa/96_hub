from flask import Flask, flash, redirect, render_template, request, session, url_for


app = Flask(__name__)

if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

@app.route('/')
@nocache
def main():
	"""Show main page"""
	"""At the very least, we will need to pass device ID,
	patient information for every device."""
    return render_template("main.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


