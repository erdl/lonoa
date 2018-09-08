"""
This module defines the sqlalchemy ORM that stores database insertion success and readings
"""

from sqlalchemy import create_engine
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func

import csv
import os

#needs to be global so ORM classes can be initialized
BASE = declarative_base()
DB_URL = 'postgresql:///egauge'

class Reading(BASE):
    """
    This class represents the database_insertion_timestamp table

    The table contains data read by the sensor for given units of time (usually minutes)

    Columns:
        reading_id: uniquely identifies a reading
        sensor_id: the id of the egauge sensor that made the reading
        timestamp: the reading's timestamp
        units: corresponds to the column name of the reading
        as obtained in its api request
        reading: the numerical value of a reading
        upload_timestamp: the time when the api request was made;
        floored to the nearest minute
    """

    __tablename__ = 'reading'

    reading_id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer)
    timestamp = Column(TIMESTAMP)
    units = Column(String)
    reading = Column(DOUBLE_PRECISION)
    upload_timestamp = Column(TIMESTAMP)

class DatabaseInsertionTimestamp(BASE):
    """
    This class represents the database_insertion_timestamp table

    Columns:
        id: uniquely identifies a row
        timestamp: the last time an api request was called
        is_success: represents if the request was successful
    """

    __tablename__ = 'database_insertion_timestamp'

    # the sqlalchemy orm requires a primary key in each table
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP)
    is_success = Column(Boolean)

    # def __repr__(self):
    #     return "<DatabaseInsertionTimestamp(id='%s', timestamp='%s, is_success='%s')>" % (
    #                          self.id, self.timestamp, self.is_success)

def setup(db_url=DB_URL):
    """
    Setup tables for testing in a given database
    """

    db = create_engine(db_url)
    Session = sessionmaker(db)
    session = Session()
    BASE.metadata.create_all(db)
    session.commit()
    session.close()

def teardown(db_url=DB_URL):
    """
    Drop each table that was set up for testing in a given database
    """

    db = create_engine(db_url)
    Reading.__table__.drop(db)
    DatabaseInsertionTimestamp.__table__.drop(db)

def export_reading_to_csv(db_url=DB_URL, output_filename='reading_dump.csv'):
    db = create_engine(db_url)
    Session = sessionmaker(db)
    session = Session()

    with open(output_filename, 'w') as outfile:
        outcsv = csv.writer(outfile)
        rows = session.query(Reading)
        for row in rows:
            outcsv.writerow([row.reading_id, row.sensor_id, row.timestamp, row.units, row.reading])
    session.close()
