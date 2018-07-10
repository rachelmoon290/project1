import os

from flask import Flask, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
    return render_template("index.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signupsuccess", methods=["POST"])
def signupsuccess():
    id = request.form.get("id")
    password = request.form.get("password")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")

    if db.execute("SELECT * FROM users WHERE login_id = :id", {"id": id}).rowcount == 1:
        return render_template("error.html", message="ID already exists. Please sign up using a different ID.", url="signup")
    db.execute("INSERT INTO users (login_id, password, firstname, lastname) VALUES (:a, :b, :c, :d)", {"a": id, "b": password, "c": firstname, "d": lastname})
    db.commit()
    return render_template("signupsuccess.html", id = id)


@app.route("/usermain", methods=["POST"])
def usermain():
    id = request.form.get("id")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE login_id = :id", {"id": id}).rowcount == 0:
        return render_template("error.html", message="ID does not exist. Please try again.", url="login")
    elif db.execute("SELECT * FROM users WHERE login_id = :id AND password = :pw", {"id": id, "pw": password}).rowcount == 1:
        return render_template("usermain.html", id = id)
    else:
        return render_template("error.html", message="Wrong password. Please try again.", url="login")


@app.route("/locations", methods=["POST"])
def locations():
    search = request.form.get("search").upper()
    if search == '' or None:
        return render_template("error.html", message = "Please type at least one character to search for your location.", url = "usermain")

    #if no match, return error
    if db.execute("SELECT * FROM location WHERE zipcode LIKE :search OR city LIKE :search OR state LIKE :search", {"search": '%' + search + '%'}).rowcount == 0:
        return render_template("error.html", message = "There were no matches. Please search again!", url="usermain")

    locs = db.execute("SELECT * FROM location WHERE zipcode LIKE :search OR city LIKE :search OR state LIKE :search", {"search": '%' + search + '%'}).fetchall()
    return render_template("locations.html", results = locs)


@app.route("/locations/<int:location_id>")
# need to make sure only logged in people can see this
def location(location_id):

    location_info = db.execute("SELECT * FROM location WHERE id = :x", {"x": location_id}).fetchone()
    checkin_info = db.execute("SELECT * FROM checkin WHERE loc = :a", {"a": location_id}).fetchall()
    count = db.execute("SELECT login_id FROM checkin").rowcount
    return render_template("location.html", location = location_info, checkins = checkin_info, count = count)




'''
@app.route("/checkin_submission", methods=["POST"])
def checkin_submission():
    login_id =
    loc =
    comment = request.form.get("comment")

    db.execute("INSERT INTO checkin (login_id, loc, comment) VALUES (:a, :b, :c)", {"a": login_id, "b": loc, "c": comment})
    db.commit()
    return render_template("checkin_submission.html")
'''
