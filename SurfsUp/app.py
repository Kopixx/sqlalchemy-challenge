#Import required packages
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy import create_engine, func, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

import numpy as np
import datetime as dt
from datetime import datetime

#Create engine
engine = create_engine("sqlite:///hawaii.sqlite")

#Declare base
Base = automap_base()

#Reflect database
Base.prepare(autoload_with=engine)

#Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create app instance
app = Flask(__name__)

#Create index route
@app.route("/")
def home():
    print("Server request for index route...")
    return(
        f"Module 10 Challenge by Kali Notaras <br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"For date-specific searches, use format 'YYYY-MM-DD':<br/>"
        f"/api/v1.0/'start_date'<br/>"
        f"/api/v1.0/'start_date'/'end_date'"
    )

#Create precipitation route
@app.route("/api/v1.0/precipitation")
def precp():
    print("Server request for precipitation route...")

    #Create session link
    session = Session(engine)

    #Query all precipitation results
    precipiation_dates = session.query(Measurement.date, Measurement.prcp).all()

    #Close session
    session.close()

    #Save query into a list of dictionaries
    all_precipitation = []

    for date, prcp in precipiation_dates:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)

    #Return jsonified result
    return jsonify(all_precipitation)

#Create stations route
@app.route("/api/v1.0/stations")
def stations():
    print("Server request for stations route...")

    #Create session link
    session = Session(engine)

    #Query all stations
    stations = session.query(Station.station).distinct().all()

    #Close session
    session.close()

    #Convert tuple list into normal list
    stations_list = list(np.ravel(stations))

    #Return jsonified result
    return jsonify(stations_list)

#Create temperature route
@app.route("/api/v1.0/tobs")
def tobs():
    print("Server request for tobs route...")

    #Create session link
    session = Session(engine)

    #Query for most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    #Isolate the most active station id
    most_active = active_stations[0][0]

    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = datetime.strptime(recent_date[0], '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    year_date = recent_date - dt.timedelta(days=365)    

    #Query all tobs
    tobs = session.query(Measurement.tobs).filter(Measurement.station == most_active).\
        filter(Measurement.date >= year_date).order_by(Measurement.date).all()

    #Close session
    session.close()

    #Convert tuple list into normal list
    tobs_list = list(np.ravel(tobs))

    #Return jsonified result
    return jsonify(tobs_list)

#Create temp summary from start date
@app.route("/api/v1.0/<start>")
def temp_start(start):
    print("Server request for start route...")

    #Convert the entry to datetime format
    start_date = datetime.strptime(start, '%Y-%m-%d')

    #Create session link
    session = Session(engine)

    #Query all tobs post start date
    start_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    #Close session
    session.close()

    #Save query results into dictionary
    for tmin, tavg, tmax in start_stats:
        start_dict = {}
        start_dict["Date_Start"] = start_date
        start_dict["Minimum_Temp"] = tmin
        start_dict["Average_Temp"] = tavg
        start_dict["Maximum_Temp"] = tmax

    #Return jsonified result
    return jsonify(start_dict)

#Create temp summary from start to end date
@app.route("/api/v1.0/<start>/<end>")
def temp_end(start, end):
    print("Server request for end route...")

    #Convert the entry to datetime format
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    #Create session link
    session = Session(engine)

    #Query all tobs post start date
    end_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    #Close session
    session.close()

    #Save query results into dictionary
    for tmin, tavg, tmax in end_stats:
        end_dict = {}
        end_dict["Date_Start"] = start_date
        end_dict["Date_End"] = end_date
        end_dict["Minimum_Temp"] = tmin
        end_dict["Average_Temp"] = tavg
        end_dict["Maximum_Temp"] = tmax

    #Return jsonified result
    return jsonify(end_dict)

#Define main behaviour
if __name__ == "__main__":
    app.run(debug=True)