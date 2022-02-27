from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

Base = automap_base()

# Connect to the sqlite file
engine = create_engine('sqlite:///hawaii.sqlite')

# Reflect the tables
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
session.close()
