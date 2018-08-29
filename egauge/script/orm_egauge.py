#!./env/bin/python3
"""
This module defines classes for the postgresql tables that store database insertion success and readings
and functions relating to those tables
"""
from pathlib import Path #used to read config.txt in parent directory
from sqlalchemy import create_engine
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.schema import ForeignKey

import configparser
# import csv
import os


# needs to be in the same scope as all ORM table classes because they are subclasses of declarative_base class
BASE = declarative_base()


class PipelineStage:
    """
    This class defines strings that could be inserted into error_log.pipeline_stage

    Each string represents at what stage of the api script execution an error_log row was inserted
        data_acquisition: attempting to obtain readings from source
        database_insertion: attempting to insert new rows into readings table
    """
    data_acquisition = "data_acquisition"
    database_insertion = "database_insertion"


class SensorType:
    """
    This class defines strings that could be inserted into sensor_info.sensor_type
    """
    egauge = "egauge"
    hobo = "hobo"
    webctrl = "webctrl"


class Project(BASE):
    """
    This class represents the project table

    Columns:
        project_folder_path: the full path of the folder where a project's files and folders are stored
    """
    __tablename__ = 'project'

    project_folder_path = Column(String, primary_key=True)


class Readings(BASE):
    """
    This class represents the readings table

    The table contains data read by the sensor for given units of time (usually minutes)

    Columns:
        datetime: the reading's datetime
        purpose_id: unique id representing a purpose
        value: the numerical value of a reading
    """
    __tablename__ = 'readings'

    datetime = Column(TIMESTAMP, primary_key=True)
    purpose_id = Column(Integer, primary_key=True)
    value = Column(DOUBLE_PRECISION)


class SensorInfo(BASE):
    """
    Sources of readings

    Columns:
        purpose_id: integer uniquely identifying a purpose
        sensor_id: string uniquely id'ing a sensor; used in egauge and webctrl API requests; hobo sensor serial number
            one sensor_id may have multiple purposes (egauge)
        data_sensor_info_mapping: matches full column name in raw data (egauge api data, hobo csv's, etc)
        sensor_part: string that represents one column name in data from a sensor if one row of data has multiple readings
        sensor_type: string representing how readings are accessed; e.g. egauge, webctrl, hobo
        is_active: boolean representing if script should request data from a sensor
        last_updated_datetime: postgres timestamp used to keep track of datetime of last successfully inserted reading
        unit: unit of readings
    """
    __tablename__ = 'sensor_info'

    purpose_id = Column(Integer, primary_key=True)
    sensor_id = Column(String)
    data_sensor_info_mapping = Column(String)
    sensor_part = Column(String)
    sensor_type = Column(String)
    is_active = Column(Boolean)
    last_updated_datetime = Column(TIMESTAMP)
    unit = Column(String)


class ErrorLog(BASE):
    """
    This class represents the error_log table

    This table is the "historian" of the database and should help the entire team troubleshoot problem.
    While it is not an oracle of all errors, it should help narrow down the problem space.

    2 new rows will be added to this table every time the script runs.

    Columns:
        log_id: uniquely identifies a row
        purpose_id: unique id representing a purpose
        datetime: when an api request or a reading insertion was attempted
        status: string representing if api script ran successfully or if something else happened
        error_type: name of python exception caught; should remain empty if no exception was caught
        pipeline_stage: what stage of the api script execution an error_log row was inserted
    """
    __tablename__ = 'error_log'

    # the sqlalchemy orm requires a primary key in each table
    log_id = Column(Integer, primary_key=True)
    purpose_id = Column(Integer)
    datetime = Column(TIMESTAMP)
    status = Column(Boolean)
    error_type = Column(String)
    pipeline_stage = Column(String)

    # def __repr__(self):
    #     return "<ErrorLog(id='%s', timestamp='%s, is_success='%s')>" % (
    #                          self.id, self.timestamp, self.is_success)


class ErrorLogDetails(BASE):
    """
    This class represents the error_log_details table that houses any extra info needed to troubleshoot script problems.

    error_log_details is a long-form table.
    It is currently used with hobo scripts to store filename, first and last reading timestamps,
    as one hobo has multiple files, with potentially repeated names.
    """
    __tablename__ = 'error_log_details'

    log_id = Column(Integer, primary_key=True)
    information_type = Column(String, primary_key=True)
    information_value = Column(String)


class ApiAuthentication(BASE):
    """
    User info for authentication

    Currently used to connect to webctrl api
    """
    __tablename__ = 'api_authentication'

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)


def setup():
    """
    Setup tables for testing in a given database
    """
    config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent) + "/config.txt"
    with open(config_path, "r") as file:
        #prepend '[DEFAULT]\n' since ConfigParser requires section headers in config files
        config_string = '[DEFAULT]\n' + file.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    db_url = "postgresql:///" + config['DEFAULT']['db']
    db = create_engine(db_url)
    BASE.metadata.create_all(db)


def teardown():
    """
    Drop each table that was set up for testing in a given database
    """
    config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent) + "/config.txt"
    with open(config_path, "r") as file:
        #prepend '[DEFAULT]\n' since ConfigParser requires section headers in config files
        config_string = '[DEFAULT]\n' + file.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    db_url = "postgresql:///" + config['DEFAULT']['db']
    db = create_engine(db_url)
    BASE.metadata.drop_all(db)
    # Readings.__table__.drop(db) # how to drop one table

# def export_reading_to_csv(db_url=DB_URL, output_filename='reading_dump.csv'):
#     db = create_engine(db_url)
#     Session = sessionmaker(db)
#     session = Session()
#
#     with open(output_filename, 'w') as outfile:
#         outcsv = csv.writer(outfile)
#         rows = session.query(Reading)
#         for row in rows:
#             outcsv.writerow([row.reading_id, row.sensor_id, row.timestamp, row.units, row.reading])
#     session.close()
