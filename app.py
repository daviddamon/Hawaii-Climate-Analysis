# sqlalchemy-challenge

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import datetime as dt
from datetime import timedelta

# import Flask
from flask import Flask
from flask import Flask, jsonify

############################################################
# Database Setup
############################################################

# create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

############################################################
# Flask
############################################################

# create an app, being sure to pass __name__
app = Flask(__name__)

############################################################
# Welcome route
############################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate Home Page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

############################################################
# Precipitation route
############################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all dates and precipitation values"""
    
    # query all dates
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()

    session.close()

    # convert list of tuples into normal list
    all_precip = list(np.ravel(results))

    # create a dictionary from the row data and append to a list of all_passengers
    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

############################################################
# Station route
############################################################

@app.route("/api/v1.0/stations")
def stations():
    # create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all weather stations"""

    # query all stations
    results = session.query(Station.station).\
        order_by(Station.station).all()

    session.close()

    # convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

############################################################
# TOBs route
############################################################

@app.route("/api/v1.0/tobs")
def tobs():
    # create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all TOBs"""

    # determine date range for last year of data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # find most active station
    readings_per_station = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()

    most_active = readings_per_station[0][0]

    # query all tobs
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date).all()

    session.close()

    # convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)

############################################################
# Start Date route
############################################################

@app.route("/api/v1.0/<startdate>")
def start_date_data(startdate):
    # create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of TMIN, TAVG, and TMAX tob values after start date"""
    
    # query all tobs
    results = session.query(func.min(Measurement.tobs),\
        func.avg (Measurement.tobs),\
        func.max (Measurement.tobs)).\
        filter(Measurement.date >= startdate).\
        filter(Measurement.station == ('most_active')).all()
    
    session.close()

    # convert list of tuples into normal list
    tob_list = list(np.ravel(results))

    # create a dictionary from the row data and append to a list of all_passengers
    tob_list = []
    for min, avg, max in results:
        tob_list_dict = {}
        tob_list_dict["TMIN"] = min
        tob_list_dict["TAVG"] = avg
        tob_list_dict["TMAX"] = max
        tob_list.append(tob_list_dict)

    return jsonify(tob_list)

############################################################
# Start and End Date route
############################################################

@app.route("/api/v1.0/<startdate>/<enddate>")
def date_range_data(startdate,enddate):
    # create session (link) from Python to the DB
    session = Session(engine)

    """Return a list of TMIN, TAVG, and TMAX tob values for date range"""
    
    # query all tobs
    results = session.query(func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= startdate).\
        filter(Measurement.date <= enddate).\
        filter(Measurement.station == ('most_active')).all()

    session.close()

    # convert list of tuples into normal list
    date_range_tobs = list(np.ravel(results))

    # create a dictionary from the row data and append to a list of all_passengers
    date_range_tobs = []
    for min, avg, max in results:
        date_range_tobs_dict = {}
        date_range_tobs_dict["TMIN"] = min
        date_range_tobs_dict["TAVG"] = avg
        date_range_tobs_dict["TMAX"] = max
        date_range_tobs.append(date_range_tobs_dict)

    return jsonify(date_range_tobs)

############################################################
# define main behavior
############################################################

if __name__ == "__main__":
    app.run(debug=True)
