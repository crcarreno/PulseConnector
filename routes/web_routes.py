from routes.api_routes import app
from flask import render_template

@app.route("/")
def home():
    return "test"
    #return render_template("index.html")

@app.route("/index")
def index():
    return render_template("index.html")
