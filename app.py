from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import datetime as dt
import os
print(os.getcwd())

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# View all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    output = (
        "/<br>" 
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/&ltstart&gt<br>"
        "/api/v1.0/&ltstart&gt/&ltend&gt"
    )
    return output

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    # Perform a query to retrieve the data and precipitation scores
    date_and_perc = session.query(Measurement.prcp, Measurement.date).all()
    session.close()
    # Create a for loop and dictionary
    # Make an empty list to append the scores
    date_and_perc_list = []
    for prcp, date in date_and_perc:
        new_dict = {}
        new_dict['precipitation'] = prcp
        new_dict['date'] = date
        date_and_perc_list.append(new_dict)
    return jsonify(date_and_perc_list)

@app.route("/api/v1.0/stations")
def station():
    # Create session
    session = Session(engine)

    #Return a JSON list of stations from the dataset.
    stations = session.query(Station.station, Station.id).all()
    session.close()
    
    # Create a for loop and dictionary
    # Make an empty list to append the scores
    station_list = []
    for station, id in stations:
        station_dict = {}
        station_dict['precipitation'] = station
        station_dict['date'] = id
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #Query the dates and temperature observations of the most-active station 
    # for the previous year of data.
    most_active_last_year = session.query(Measurement.date).\
          order_by(Measurement.date.desc()).first()
    
    # Return a JSON list of temperature observations for the previous year.
    #Calculate date from 12 months prior
    # last_date_values = []
    # for date in most_active_last_year:
    #     last_year_dict = {}
    #     last_year_dict["date"] = date
    #     last_date_values.append(last_year_dict)
    last_date = dt.date(2017, 8, 18) - dt.timedelta(days = 365)

    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).group_by(Measurement.station).first()
    # Most active station is first in active_stations
    print(active_stations[0])
    session.close()

    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.station == active_stations[0]).\
        filter(Measurement.date > last_date).all()
    
    # Create for loop and empty list to append dictionary
    result_vals = []
    for date, tobs, station in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_dict['station'] = station
        result_vals.append(tobs_dict)
    
    return jsonify(result_vals)


@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the maximum temperature for a specified start range.
    # format the datetime
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    start_tobs = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),\
                  func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    session.close()

    #Create an empty list and for loop to append dictionary
    start_tobs_vals = []
    for tmin, avg, tmax in start_tobs:
        start_tobs_dict = {}
        start_tobs_dict["min"] = tmin
        start_tobs_dict["avg"] = avg
        start_tobs_dict["max"] = tmax
        start_tobs_vals.append(start_tobs_dict)
    return jsonify(start_tobs_vals)
    

# Return a JSON list of the minimum temperature, the average temperature, 
# and the maximum temperature for a specified start-end range.
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    # format the datetime
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    start_end_tobs = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),\
                  func.max(Measurement.tobs)).filter(Measurement.date >= start_date).\
                  filter(Measurement.date <= end_date).all()
    session.close()

    start_end_tobs_vals = []
    for tmin, tavg, tmax in start_end_tobs:
        start_end_tobs_dict = {}
        start_end_tobs_dict["min_temp"] = tmin
        start_end_tobs_dict["avg_temp"] = tavg
        start_end_tobs_dict["max_temp"] = tmax
        start_end_tobs_vals.append(start_end_tobs_dict) 
    return jsonify(start_end_tobs_vals)


if __name__ == "__main__":
    app.run(debug=True)
