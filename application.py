import os, requests

from flask import Flask, render_template, request, session, redirect, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from decimal import Decimal
import pandas

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


@app.route("/signup")
def signup():
    session.clear()
    return render_template("signup.html")


@app.route("/login")
def login():
    session.clear()
    return render_template("login.html")


@app.route("/signupsuccess", methods=["POST"])
def signupsuccess():
    id = request.form.get("id")
    password = request.form.get("password")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")

    if db.execute("SELECT * FROM users WHERE login_id = :id", {"id": id}).rowcount == 1:
        return render_template("error.html", message="ID already exists. Please sign up using a different ID.", url="signup", button = "Go back to signup")
    db.execute("INSERT INTO users (login_id, password, firstname, lastname) VALUES (:a, :b, :c, :d)", {"a": id, "b": password, "c": firstname, "d": lastname})
    db.commit()
    return render_template("signupsuccess.html", id = id)


@app.route("/usermain", methods=["POST", "GET"])
def usermain():
    if session.get("location_result") is not None:
        session.pop("location_result", None)
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE login_id = :id AND password = :pw", {"id": id, "pw": password}).rowcount == 1:
            session["user_id"] = id
            return render_template("usermain.html", id = id)
        else:
            return render_template("error.html", message="ID and password does not match. Please try again.", url="login", button = "Go back to login")
    else:
        if session.get("user_id") is None:
            return redirect("/")
        else:
            id = session.get("user_id")
            return render_template("usermain.html", id = id)


@app.route("/locations", methods=["POST"])
def locations():
    search = request.form.get("search").upper()
    search = str(search)
    if search == '' or None:
        return render_template("error.html", message = "Please type at least one character to search for your location.", url = "usermain", button = "Go back to search")

    #if no match, return error
    if db.execute("SELECT * FROM location WHERE zipcode LIKE :search OR city LIKE :search OR state LIKE :search", {"search": '%' + search + '%'}).rowcount == 0:
        return render_template("error.html", message = "There were no matches. Please search again!", url="usermain", button = "Go back to search")

    locs = db.execute("SELECT * FROM location WHERE zipcode LIKE :search OR city LIKE :search OR state LIKE :search", {"search": '%' + search + '%'}).fetchall()
    return render_template("locations.html", results = locs)


@app.route("/locations/<int:location_id>")
def location(location_id):
    if session.get("user_id") is None:
        return render_template("error.html", message = "Invalid access. Please log in.", url = "login", button = "Log In")
    session["location_result"] = location_id
    location_info = db.execute("SELECT * FROM location WHERE id = :x", {"x": location_id}).fetchone()
    checkin_info = db.execute("SELECT * FROM checkin WHERE loc = :a", {"a": location_id}).fetchall()
    count = db.execute("SELECT login_id FROM checkin WHERE loc = :a", {"a": location_id}).rowcount

    weather_info = requests.get(f"https://api.darksky.net/forecast/d86b65085b6b96eb4d6593f275189892/{location_info.latitude},{location_info.longitude}")
    weather_info = weather_info.json()

    weather_time = pandas.to_datetime(weather_info["currently"]["time"],unit='s')

    return render_template("location.html", location = location_info, checkins = checkin_info, count = count, weather = weather_info, time = weather_time)


@app.route("/checkin_submission", methods=["POST"])
def checkin_submission():
    login_id = session.get("user_id")
    loc = session.get("location_result")
    comment = request.form.get("comment")

    if db.execute("SELECT * FROM checkin JOIN users ON users.id = checkin.login_id WHERE users.login_id = :x AND loc = :y", {"x": login_id, "y": loc}).rowcount == 1:
        return render_template("error.html", message = "You have already checked in to this location.", url = "usermain", button = "Go back to homepage")
    else:
        user_id_num = db.execute("SELECT id FROM users WHERE login_id = :x", {"x": login_id}).fetchone()
        db.execute("INSERT INTO checkin (login_id, loc, comment) VALUES (:a, :b, :c)", {"a": user_id_num[0], "b": loc, "c": comment})
        db.commit()
        return render_template("checkin_submission.html")


@app.route("/api/locations/<string:zipcode>")
def location_api(zipcode):

    if db.execute("SELECT zipcode FROM location WHERE zipcode = :x", {"x": zipcode}).rowcount == 0:
        abort(404)

    location_info = db.execute("SELECT * FROM location WHERE zipcode = :x", {"x": zipcode}).fetchone()
    count = db.execute("SELECT login_id FROM checkin WHERE loc = :a", {"a": location_info.id}).rowcount
    count = Decimal(count)

    return jsonify({
            "place_name": location_info.city.title(),
            "state": location_info.state,
            "latitude": location_info.latitude,
            "longitude": location_info.longitude,
            "zip": location_info.zipcode,
            "population": location_info.population,
            "check_ins": count
        })
