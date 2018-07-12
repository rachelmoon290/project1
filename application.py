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



'''Website Routes'''


# Homepage (before login)
@app.route("/")
def index():
    # remove all sessions if redirected back to the homepage
    session.clear()
    return render_template("index.html")


# Sign-up Page
@app.route("/signup")
def signup():
    # remove all sessions if user visits this page
    session.clear()
    return render_template("signup.html")


# Sign-up Success Page
@app.route("/signupsuccess", methods=["POST"])
def signupsuccess():
    #retrieve user information from the sign-up form tne new user submitted
    id = request.form.get("id")
    password = request.form.get("password")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")

    # if user leaves anything in the form blank, throw error and ask them to try signing up again
    if id or password or firstname or lastname == '' or None:
        return render_template("error.html", message = "Please fill all sections of the form to sign up.", url = "signup", button = "Go Back")

    # if ID already exists in the users database, throw error page and ask users to sign up using different ID
    if db.execute("SELECT * FROM users WHERE login_id = :id", {"id": id}).rowcount == 1:
        return render_template("error.html", message="ID already exists. Please sign up using a different ID.", url="signup", button = "Go Back")

    # add user information to the users database
    db.execute("INSERT INTO users (login_id, password, firstname, lastname) VALUES (:a, :b, :c, :d)", {"a": id, "b": password, "c": firstname, "d": lastname})
    db.commit()
    return render_template("signupsuccess.html", id = id)


# Login Page
@app.route("/login")
def login():
    #remove all sessions if user visits this page
    session.clear()
    return render_template("login.html")


# Main Page (Home Page for logged in users)
@app.route("/usermain", methods=["POST", "GET"])
def usermain():

    # if users revisit this page after location search, clear session info about the previous location search
    if session.get("location_result") is not None:
        session.pop("location_result", None)

    # if users are visiting this page by logging in, retrieve their ID and password input information
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")

        # if ID and password match, store session id information, and allow users to enter the user main page
        if db.execute("SELECT * FROM users WHERE login_id = :id AND password = :pw", {"id": id, "pw": password}).rowcount == 1:
            session["user_id"] = id
            return render_template("usermain.html", id = id)

        #if ID and password do not match, throw error message and ask users to try logging in again
        else:
            return render_template("error.html", message="ID and password do not match. Please try again.", url="login", button = "Go Back")

    #if users are visiting this page by GET request, if they are not logged in (by checking their session id information), redirect them to Homepage
    else:
        if session.get("user_id") is None:
            return redirect("/")

        #if the users are already logged in, and want to revisit this page, allow them to access the page
        else:
            id = session.get("user_id")
            return render_template("usermain.html", id = id)


# Locations Results Page
@app.route("/locations", methods=["POST"])
def locations():

    # retrieve user search input data as string type
    search = request.form.get("search").upper()
    search = str(search)

    # if user didn't write anything in the search box, throw error and ask them to try searching again with an input
    if search == '' or None:
        return render_template("error.html", message = "Please type at least one character to search for your location.", url = "usermain", button = "Search Again")

    # if there was no match, throw error
    if db.execute("SELECT * FROM location WHERE zipcode LIKE :search OR city LIKE :search OR state LIKE :search", {"search": '%' + search + '%'}).rowcount == 0:
        return render_template("error.html", message = "There were no matches. Please search again!", url="usermain", button = "Go back to Search")

    # search from the database to see if zipcode/city/state matches with the user input, and retrieve results
    locs = db.execute("SELECT * FROM location WHERE zipcode LIKE :search OR city LIKE :search OR state LIKE :search", {"search": '%' + search + '%'}).fetchall()
    return render_template("locations.html", results = locs)


# Location Page
@app.route("/locations/<int:location_id>")
def location(location_id):
    # prevent users who are not logged in from viewing this page, and redirect them to login page
    if session.get("user_id") is None:
        return render_template("error.html", message = "Invalid access. Please log in.", url = "login", button = "Log In")

    # store location id in the session, and retrieve location information from checkin and location database
    session["location_result"] = location_id
    location_info = db.execute("SELECT * FROM location WHERE id = :x", {"x": location_id}).fetchone()
    checkin_info = db.execute("SELECT * FROM checkin WHERE loc = :a", {"a": location_id}).fetchall()
    count = db.execute("SELECT login_id FROM checkin WHERE loc = :a", {"a": location_id}).rowcount

    # get weather information about this location from DarkSky API
    weather_info = requests.get(f"https://api.darksky.net/forecast/d86b65085b6b96eb4d6593f275189892/{location_info.latitude},{location_info.longitude}")
    weather_info = weather_info.json()
    weather_time = pandas.to_datetime(weather_info["currently"]["time"],unit='s')

    return render_template("location.html", location = location_info, checkins = checkin_info, count = count, weather = weather_info, time = weather_time)


# Checkin Submission Page
@app.route("/checkin_submission", methods=["POST"])
def checkin_submission():

    #retrieve information about the user id, location, and checkin comments
    login_id = session.get("user_id")
    loc = session.get("location_result")
    comment = request.form.get("comment")

    # if user has already checked into this location before, throw an error
    if db.execute("SELECT * FROM checkin JOIN users ON users.id = checkin.login_id WHERE users.login_id = :x AND loc = :y", {"x": login_id, "y": loc}).rowcount == 1:
        return render_template("error2.html", message = "You have already checked in to this location.", url = "location", location_id = loc, button = "Go Back")

    # add user's checkin information into checkin database
    else:
        user_id_num = db.execute("SELECT id FROM users WHERE login_id = :x", {"x": login_id}).fetchone()
        db.execute("INSERT INTO checkin (login_id, loc, comment) VALUES (:a, :b, :c)", {"a": user_id_num[0], "b": loc, "c": comment})
        db.commit()
        return render_template("checkin_submission.html", location_id = loc)


# API Access Page
@app.route("/api/locations/<string:zipcode>")
def location_api(zipcode):
    # if zipcode does not exist in the location database, throw 404 error
    if db.execute("SELECT zipcode FROM location WHERE zipcode = :x", {"x": zipcode}).rowcount == 0:
        abort(404)

    # retrieve location information from location and checkin database
    location_info = db.execute("SELECT * FROM location WHERE zipcode = :x", {"x": zipcode}).fetchone()
    count = db.execute("SELECT login_id FROM checkin WHERE loc = :a", {"a": location_info.id}).rowcount
    count = Decimal(count)

    # return retrieved information
    return jsonify({
            "place_name": location_info.city.title(),
            "state": location_info.state,
            "latitude": location_info.latitude,
            "longitude": location_info.longitude,
            "zip": location_info.zipcode,
            "population": location_info.population,
            "check_ins": count
        })
