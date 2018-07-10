import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#In terminal I set environmental variable DATABASE_URL = postgres://ulhnqlccgocmja:b782a00b3f5360ceec74421436c409e7fe72f1a945058271d0e7dc96e5dd1113@ec2-107-21-95-70.compute-1.amazonaws.com:5432/d79kdcuj6gsi9t
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    #create user table in the database
    db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, login_id VARCHAR NOT NULL, password VARCHAR NOT NULL, firstname VARCHAR NOT NULL, lastname VARCHAR NOT NULL)")

    #create checkin table in the database
    db.execute("CREATE TABLE checkin (id SERIAL PRIMARY KEY, login_id INTEGER REFERENCES users, loc INTEGER REFERENCES location, comment VARCHAR)")

    # apply changes to the database
    db.commit()

if __name__ == "__main__":
      main()
