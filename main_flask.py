from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta

# Initialize Flask instance
app = Flask(__name__)

# Initialize API constant for version 1.0
API_VER_1 = "/api/1.0"

# Initialize sqlite database
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


@app.route("/")
def home_page():
    """
    The home page, lists all routes that are available.
    :return:
    """
    routes_list = [
        f"{API_VER_1}/precipitation",
        f"{API_VER_1}/stations",
        f"{API_VER_1}/tobs"
    ]

    list_items = []
    for route in routes_list:
        list_item = f"<li>{route}</li>"
        list_items.append(list_item)

    return "<br/>".join(routes_list)

@app.route(f"{API_VER_1}/precipitation")
def precipitation():
    """
    Return list of all precipitation data
    :return:
    """
    session = Session(bind=engine)
    statement = f"SELECT date, prcp from MEASUREMENT"
    result = session.execute(statement).all()
    session.close()

    result_list = []
    for row in result:
        data = {
            "Date": row[0],
            "Prcp": row[1]
        }
        result_list.append(data)

    return jsonify(result_list)

@app.route(f"{API_VER_1}/stations")
def stations():
    """
    Return list of all stations data
    :return:
    """
    session = Session(bind=engine)
    statement = f"SELECT station FROM station"
    result = session.execute(statement).all()
    session.close()
    result = list(np.ravel(result))
    return jsonify(result)

@app.route(f"{API_VER_1}/tobs")
def tobs():
    """
    Query the dates and temperature observations of the most active station for the last year of data.
    Return a JSON list of temperature observations (TOBS) for the previous year.
    :return:
    """
    # Start session and query most active station
    session = Session(bind=engine)
    statement = "SELECT station, COUNT(*) AS occurrences FROM measurement GROUP BY station ORDER BY occurrences DESC"
    highest_station_id = session.execute(statement).first()[0]
    session.close()

    # Get the most recent date and convert it into a datetime object
    statement = f"SELECT MAX(date) FROM measurement"
    latest_date = session.execute(statement).all()[0][0]
    latest_date_parts = str(latest_date).split("-")
    year = int(latest_date_parts[0])
    month = int(latest_date_parts[1])
    day = int(latest_date_parts[2])
    latest_date = dt.datetime(year, month, day)

    # Calculate the time delta of the last 12 months from the latest date
    twelve_months_ago = latest_date + relativedelta(months=-12)

    # Filter by the station with the highest number of observations
    # [0] index, [1] station id, [2] date, [3] prcp, [4] tobs
    statement = f"""SELECT station, date, tobs
                FROM measurement
                WHERE date > '{twelve_months_ago}'
                AND station = '{highest_station_id}'
                ORDER BY date DESC"""
    result = session.execute(statement).all()
    session.close()
    result_dict = []
    for row in result:
        data = {
            "Station": row[0],
            "Date": row[1],
            "Temp": row[2]
        }
        result_dict.append(data)
    return jsonify(result_dict)

@app.route(f"{API_VER_1}/<start>")
def start_route(start):
    """
    Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start
    or start-end range.

    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    :param start:
    :return:
    """
    # Get the start date from the route
    start_date = start

    # Start session
    session = Session(bind=engine)
    result = session.query(
                func.min(Measurement.tobs),
                func.max(Measurement.tobs),
                func.avg(Measurement.tobs))\
        .filter(Measurement.date > start_date).all()[0]
    session.close()
    result_dict = {
        "min_temp": result[0],
        "max_temp": result[1],
        "avg_temp": result[2]
    }
    return jsonify(result_dict)

@app.route(f"{API_VER_1}/<start>/<end>")
def start_and_end_route(start, end):
    """
    Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start
    or start-end range.

    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and
    end date inclusive.
    :param start:
    :param end:
    :return:
    """
    # Get the start and end date from the route
    start_date = start
    end_date = end

    # Start session
    session = Session(bind=engine)
    result = session.query(
                func.min(Measurement.tobs),
                func.max(Measurement.tobs),
                func.avg(Measurement.tobs))\
        .filter(Measurement.date > start_date)\
        .filter(Measurement.date < end_date)\
        .all()[0]
    session.close()
    result_dict = {
        "min_temp": result[0],
        "max_temp": result[1],
        "avg_temp": result[2]
    }
    return jsonify(result_dict)
