import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#In terminal I set environmental variable DATABASE_URL = postgres://ulhnqlccgocmja:b782a00b3f5360ceec74421436c409e7fe72f1a945058271d0e7dc96e5dd1113@ec2-107-21-95-70.compute-1.amazonaws.com:5432/d79kdcuj6gsi9t
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    #create table in the database
    db.execute("CREATE TABLE location (id SERIAL PRIMARY KEY, zipcode CHAR(5) NOT NULL, city VARCHAR NOT NULL, state VARCHAR NOT NULL, latitude DECIMAL NOT NULL, longitude DECIMAL NOT NULL, population INTEGER NOT NULL)")

    # open and read zipcode location file, skipping header
    f = open('zips.csv')
    next(f)
    loc_file = csv.reader(f)

    # iterate over the rows in the zipcode location file
    for row in loc_file:
        db.execute("INSERT INTO location (zipcode, city, state, latitude, longitude, population) VALUES (:x, :y, :z, :r, :v, :f)",
                      {"x": str(row[0]).zfill(5), "y": row[1], "z": row[2], "r": row[3], "v": row[4], "f": row[5]})
    # commit changes made and apply changes to the database
    db.commit()

if __name__ == "__main__":
      main()
