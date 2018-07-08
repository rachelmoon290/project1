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

    elif db.execute("SELECT * FROM users WHERE login_id = :id and password = :pw", {"id": id, "pw": password}).rowcount == 1:
        return render_template("usermain.html", id = id)

    else return render_template("error.html", message="Wrong password. Please try again.", url="login")









'''
    # Make sure flight exists.
    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        return render_template("error.html", message="No such flight with that id.")

    # If the flight exists, record the passenger as having registered for the flight.
    db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
            {"name": name, "flight_id": flight_id})

    # All done booking!
    db.commit()
    return render_template("success.html")

    '''
