import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (        
        f"Avalable Routes:<br/>"
        
        f"/api/v1.0/precipitation<br/>"
        f"- The last year of observed precipitation in the dataset.<br/>"
        f"/api/v1.0/stations"
        f"-The stations in Hawaii from the dataset.<br/>"
        f"/api/v1.0/tobs"
        f"-The temperature observations (tobs) for the last year of the dataset.<br/>"
        f"/api/v1.0/start"
        f"-A list of minimum(`TMIN`), average(`TAVG`), and maximum(`TMAX`) temperatures for all dates later than the start date (YYYY-MM-DD).<br/>"
        f"/api/v1.0/start/end"
        f"-A list of minimum(`TMIN`), average(`TAVG`), and maximum(`TMAX`) temperatures for dates between the start and end date (YYYY-MM-DD).<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    results = session.query(Measurement).all()

    measurement_results=[]
    for data in results:
        measure={}
        measure["date"]=data.date
        measure["prcp"]=data.prcp
        measurement_results.append(measure)
        
    return jsonify(measurement_results)

@app.route("/api/v1.0/stations")
def stations():

    results2 = session.query(Station).all()

    stations_results=[]
    for data in results2:
        list_stations={}
        list_stations["name"]=data.station
        stations_results.append(list_stations)
        
    return jsonify(stations_results)

@app.route("/api/v1.0/tobs")
def tobs():

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date =session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element (tuple)
    last_date = last_date[0]

    # Calculate the date 1 year ago from today
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query tobs
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list(trying something different from creating a for loop)
    tobs_list = list(results_tobs)

    return jsonify(tobs_list)

@app.route("/api/v1.0/start")
def start(start=NONE):

    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    from_start_list=list(from_start)
    
    return jsonify(from_start_list)

@app.route("/api/v1.0/start/end")
def start_end(start=NONE, end=NONE):
    
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    between_dates_list=list(between_dates)
    
    return jsonify(between_dates_list)


if __name__ == '__main__':
    app.run(debug=True)
