# Import the dependencies.
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# reflect an existing database into a new model
# reflect the tables
# Save references to each table
# Create our session (link) from Python to the DB
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station


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
        f"Welcome to the Climate App API!<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # CONNECT TO DB
    session = Session(engine)

    """Return list of precipitations"""
    #QUERY DATA
    last_measurement_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
     
    latest_date = last_measurement_data_point [0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    date_year_ago = latest_date - relativedelta(years=1)

    #QUERY DATA
    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= date_year_ago).all()
    session.close()

 # CREATE DICTIONARY
    all_precipitation = []
    for date, prcp in last_year_data:
        if prcp != None:
            precip_dict = {}
            precip_dict[date] = prcp
            all_precipitation.append(precip_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query the most active station."""
    # CONNECT TO DB
    session = Session(engine)

    #QUERY DATA
    temp_observation = session.query(
        Measurement.date).order_by(Measurement.date.desc()).first()
    
    latest_date = temp_observation [0]
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    date_year_ago = latest_date - relativedelta(years=1)

    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()

    most_active_station_id = most_active_station [0]
    print(f"The station id of the most active station is {most_active_station_id}.")

    data_from_last_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= date_year_ago).all()

    session.close()

    # CREATE DICTIONARY
    all_temperatures = []
    for date, temp in data_from_last_year:
        if temp != None:
            temp_dict = {}
            temp_dict[date] = temp
            all_temperatures.append(temp_dict)
    # Return the JSON representation of dictionary.
    return jsonify(all_temperatures)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # CONNECT TO DB
    session = Session(engine)

    #QUERY DATA
    stations = session.query(Station.station, Station.name,
                             Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # CREATE DICTIONARY
    all_stations = []
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def determine_temps_for_date_range(start, end):
    """JSON list of the min, avg, & max temp range."""

    # CONNECT TO DB
    session = Session(engine)

    #QUERY DATA
    #START & END DATE
    if end != None:
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(
            Measurement.date <= end).all()
    #START DATE ONLY.
    else:
        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    session.close()

    # CREATE LIST
    temperature_list = []
    no_temperature_data = False
    for min_temp, avg_temp, max_temp in temperature_data:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_temperature_data = True
        temperature_list.append(min_temp)
        temperature_list.append(avg_temp)
        temperature_list.append(max_temp)
    if no_temperature_data == True:
        return f"No data found for the given date(s)"
    else:
        return jsonify(temperature_list)


if __name__ == '__main__':
    app.run(debug=True)