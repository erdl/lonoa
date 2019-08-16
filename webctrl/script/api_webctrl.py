#!../../egauge/script/env/bin/python3
"""
This script attempts to obtain sensor readings from the webctrl api

and reshape and insert those readings into a database.
It also uses an error_log table to store information about those attempts.
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# import json #used if we want to output json file
import configparser
import logging
import orm_webctrl
import os
import pendulum
import requests


logging.basicConfig(filename='error.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


# connect to database by creating a session
# def get_db_handler(db_url='postgresql:///sensors'):
def get_db_handler():
    """
    1. get database name from text file "config.txt" in parent directory of webctrl/script/
    2. create a sqlalchemy engine for database using database url
    3. use sqlalchemy sessionmaker to create Session object from engine
    4. create an instance of Session called conn (represents database "connection")
    """
    # get path of config file located in parent of parent directory
    config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent) + "/config.txt"
    with open(config_path, "r") as file:
        #prepend '[DEFAULT]\n' since ConfigParser requires section headers in config files
        config_string = '[DEFAULT]\n' + file.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    db_url = "postgresql:///" + config['DEFAULT']['db']
    db = create_engine(db_url)
    Session = sessionmaker(db)
    conn = Session()
    return conn


# returns the last_updated_datetime and the readings after a successful api call
#def get_readings_from_webctrl_api(conn, query_string):
def get_data_from_api(sensor, conn):
    """
    1. build webctrl api request using sensor.query_string and sensor.last_updated_datetime from sensor_info table
    2. send request to webctrl api and attempt to download the readings data

    3. generate timestamp of data request
    4. use sensor.purpose_id to insert success or failure was_success in error_log
    """
    current_time = pendulum.now('Pacific/Honolulu')
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    # if no timestamp is found, raise exception
    if not sensor.last_updated_datetime:
        raise Exception('No last_updated_datetime found')
    #get webctrl user information
    webctrl_user_row = conn.query(orm_webctrl.ApiAuthentication.username, orm_webctrl.ApiAuthentication.password).first()
    # returns a TypeError if there are no users in database
    api_user = webctrl_user_row[0]
    api_pass = webctrl_user_row[1]
    host = 'http://www.soest.hawaii.edu/hneienergy/bulktrendserver/read'
    start_date = pendulum.instance(sensor.last_updated_datetime).to_date_string()
    #use current time to extract end date
    end_date = current_time.to_date_string()
    if start_date > end_date:
        raise ValueError('Error: start_date ' + start_date + ' was later than end_date ' + end_date)
    output_format = 'json'
    params = {'id': sensor.query_string, 'start': start_date, 'end': end_date, 'format': output_format}
    auth = (api_user, api_pass)
    readings = requests.post(host, params=params, auth=tuple(auth))
    if readings.status_code == requests.codes.ok:
        print('API request was successful' + str(readings))
        error_log_row = orm_webctrl.ErrorLog(datetime=current_time, was_success=True, purpose_id=sensor.purpose_id, pipeline_stage=orm_webctrl.ErrorLog.PipelineStageEnum.data_acquisition)
        conn.add(error_log_row)
        conn.commit()
        return readings
    else:
        readings.raise_for_status()


#def insert_webctrl_readings_into_db(conn, readings, sensors):
def insert_readings_into_database(conn, readings, sensor):
    """
    1. for each row of data, attempt to insert into readings table if datetime of row is after sensor.last_updated_datetime
        2. keep track of the latest last_updated_datetime in new_last_updated_datetime

    3. Use new_last_updated_datetime to update last_updated_datetime of current sensor in sensor_info
    4. generate timestamp of data insert attempt
    5. use purpose_id to insert success or failure of data insert attempt during step 1
    """
    current_time = pendulum.now('Pacific/Honolulu')
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    new_last_updated_datetime = ''
    rows_inserted = 0
    sensor_json_data = readings.json()
    # query_string = sensor_json_data[0]['id']
    readings = sensor_json_data[0]['s']
    #TEST
    print(str(len(readings)) + ' readings obtained', )
    for reading in readings:
        reading_time = ''
        reading_value = ''
        for key in reading.keys():
            if key is 't':
                reading_timestamp = reading[key]
                # slice off extra digits since pendulum.from_timestamp() uses 10 digit timestamps
                reading_time = pendulum.from_timestamp(int(str(reading_timestamp)[:10]))
                reading_time = reading_time.set(microsecond=reading_time.microsecond - (reading_time.microsecond % 10000))
            #'a' type values stand for analog; are like double datatypes
            #'d' type values stand for digital; are like booleans
            elif key is 'a' or key is 'd':
                reading_value = reading[key]
        # subtract 10 hours from reading time for comparison because it's GMT and last_updated_datetime is GMT - 10
        if reading_time.subtract(hours=10) > pendulum.instance(sensor.last_updated_datetime):
            reading_row = orm_webctrl.Reading(purpose_id=sensor.purpose_id, datetime=reading_time, reading=reading_value, units=sensor.unit, upload_timestamp=current_time)
            conn.add(reading_row)
            rows_inserted += 1
            new_last_updated_datetime = reading_time
    # #TEST
    # with open("output.txt", 'w') as outfile:
    #     json.dump(sensor_json_data, outfile, indent=4)
    if new_last_updated_datetime:
        conn.query(orm_webctrl.SensorInfo).filter(orm_webctrl.SensorInfo.purpose_id == sensor.purpose_id).update(
            {"last_updated_datetime": new_last_updated_datetime})
    error_log_row = orm_webctrl.ErrorLog(datetime=current_time, was_success=True, purpose_id=sensor.purpose_id, pipeline_stage=orm_webctrl.ErrorLog.PipelineStageEnum.database_insertion)
    conn.add(error_log_row)
    # need to flush and refresh to get error_log_row.log_id
    conn.flush()
    conn.refresh(error_log_row)
    # update current set of readings with related log_id
    conn.query(orm_webctrl.Reading.log_id). \
        filter(orm_webctrl.Reading.purpose_id == sensor.purpose_id,
               orm_webctrl.Reading.upload_timestamp == current_time). \
        update({'log_id': error_log_row.log_id})
    conn.commit()
    print(rows_inserted, ' row(s) inserted')


#log_failure_to_get_readings_from_webctrl_api
def log_failure_to_connect_to_api(conn, exception, sensor):
    current_time = pendulum.now('Pacific/Honolulu')
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    logging.exception('log_failure_to_connect_to_api')
    error_log_row = orm_webctrl.ErrorLog(datetime=current_time, error_type=exception.__class__.__name__, pipeline_stage=orm_webctrl.ErrorLog.PipelineStageEnum.data_acquisition, purpose_id=sensor.purpose_id, was_success=False)
    conn.add(error_log_row)
    conn.commit()


#log_failure_to_insert_webctrl_readings_into_db
def log_failure_to_connect_to_database(conn, exception, sensor):
    # rollback any db statements in conn to maintain atomicity of db insertions and updates at the purpose id level
    conn.rollback()
    current_time = pendulum.now('Pacific/Honolulu')
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    logging.exception('log_failure_to_connect_to_database')
    error_log_row = orm_webctrl.ErrorLog(datetime=current_time, error_type=exception.__class__.__name__, pipeline_stage=orm_webctrl.ErrorLog.PipelineStageEnum.database_insertion, purpose_id=sensor.purpose_id, was_success=False)
    conn.add(error_log_row)
    conn.commit()


if __name__ == '__main__':
    # connect to the database
    conn = get_db_handler()
    sensors = conn.query(orm_webctrl.SensorInfo.purpose_id, orm_webctrl.SensorInfo.query_string, orm_webctrl.SensorInfo.last_updated_datetime, orm_webctrl.SensorInfo.unit).filter_by(script_folder=orm_webctrl.SensorInfo.ScriptFolderEnum.webctrl, is_active=True)
    for sensor in sensors:
        try:
            readings = get_data_from_api(sensor, conn)
        except Exception as exception: #catch webctrl api request exceptions like requests.exceptions.ConnectionError
            log_failure_to_connect_to_api(conn, exception, sensor)
            continue
        try:
            insert_readings_into_database(conn, readings, sensor)
        except Exception as exception: #catch database exeptions like sqlalchemy.exc.InternalError, sqlalchemy.exc.OperationalError, sqlalchemy.exc.ProgrammingError, TypeError (if no users in database), psycopg2.IntegrityError(try to insert rows with duplicate keys)
            log_failure_to_connect_to_database(conn, exception, sensor)
    conn.close()
