#!./env/bin/python3
"""
This script obtains egauge readings using sensor data retrieved from a database

and inserts those readings into a readings table and a success or failure timestamp into an error_log table.

The last_updated_datetime in the sensor_info table should be set to a valid value for script to run successfully
"""
from io import StringIO
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import argparse
import configparser
import logging
import logging.handlers
import os
import pandas
import pendulum
import requests
# import sqlalchemy #used for errors like sqlalchemy.exc.InternalError, sqlalchemy.exc.OperationalError
import sys

# use grandparent_directory with sys.path.append() to import orm_lonoa from ../../ directory relatieve to this script's location
grandparent_directory = os.path.abspath(os.path.join((os.path.join(os.path.join(__file__, os.pardir), os.pardir)), os.pardir))
sys.path.append(grandparent_directory)
import orm_lonoa

SCRIPT_NAME = os.path.basename(__file__)


def set_logging_settings():
    """
    Sets logging to write ERROR messages by default to ./error.log and standard output

    Also writes INFO messages if there is a --verbose flag to ./error.log and standard output
    """
    # parser for script arguments like --verbose
    parser = argparse.ArgumentParser(description='Get reading data from egauge api and insert into database.')
    # --verbose argument is True if set
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print INFO level log messages to console and error.log')
    args = parser.parse_args()

    # set log level to INFO only if verbose is set
    if args.verbose:
        log_level = 'INFO'
    else:
        log_level = 'ERROR'

    # configure logger which will print log messages to console (only prints ERROR level messages by default; prints INFO level messages if --verbose flag is set)
    logging.basicConfig(level=log_level, format=__file__ + ': %(message)s')

    # Create a handler that writes log messages to error.log file
    # rotates error.log every time it reaches 100 MB to limit space usage; keeps up to 5 old error.log files
    rotating_file_handler = logging.handlers.RotatingFileHandler('error.log', maxBytes=100000000, backupCount=5)
    # set the message and date format of file handler
    formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    rotating_file_handler.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(rotating_file_handler)


# connect to database by creating a session
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


#THIS FUNCTION WAS DISSOLVED INTO get_data_from_api() BUT REMAINS HERE FOR REFERENCE
# # will need to update once relating each database_insertion_time to egauge sensor is decided (add filter for sensor id)
# # Obtains the latest 'success' timestamp in database_insertion_timestamp
# # which should be the the same timestamp for the last reading successfully inserted into the reading table
# def get_most_recent_timestamp_from_db(conn):
#     last_reading_timestamp = ''
#     # conn.query(func.max...)[0][0] returns the first element in the first tuple in a list
#     latest_datetime_successfully_inserted = conn.query(func.max(orm_egauge.ErrorLog.timestamp)).filter_by(is_success=True)[0][0]
#     if latest_datetime_successfully_inserted:
#         # shift timestamp 10 hours forward since HST is GMT - 10 hours
#         last_reading_timestamp = arrow.get(latest_datetime_successfully_inserted).shift(hours = +10)
#     return last_reading_timestamp


# returns a readings dataframe
#def get_readings_from_egauge_api(conn, query_string):
def get_data_from_api(conn, query_string):
    """
    1. get a list of purpose_sensors that contain purpose id, sensor mapping, and last_updated_datetime
    from sensor_info table where rows have matching query_string and are active
    2. download the data from api

    3. generate timestamp of data downloaded from api during 2 for each purpose_sensor tuple
    4. for each purpose_sensor use purpose_id from 1 to insert success or failure in error_log
    """
    current_time = pendulum.now('Pacific/Honolulu')
    # truncate time to hundredths of a second
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    # The next lines of code before setting api_start_time used to be in their own function get_most_recent_timestamp_from_db()
    purpose_sensors = conn.query(orm_lonoa.SensorInfo.purpose_id, orm_lonoa.SensorInfo.data_sensor_info_mapping, orm_lonoa.SensorInfo.last_updated_datetime, orm_lonoa.SensorInfo.unit).\
        filter_by(query_string=query_string,is_active=True)
    last_updated_datetime = purpose_sensors[0].last_updated_datetime
    if last_updated_datetime:
        # Egauge api returns readings including the start time and excluding the end time.
        # Convert last_updated_datetime from HST to GMT by adding 10 hours to get start time,
        # since last_updated_datetime is HST and egauge api uses GMT.
        # Add 60 seconds so that reading with last_updated_datetime is not reinserted.
        api_start_timestamp = pendulum.instance(last_updated_datetime).add(hours=10).add(seconds=60).int_timestamp
    else:
        raise Exception('No existing last_updated_datetime found for ', query_string)
    current_timestamp = current_time.int_timestamp
    if api_start_timestamp > current_timestamp:
        raise ValueError('Error: api_start_timestamp ' + str(api_start_timestamp) + ' was later than current_timestamp ' + str(current_timestamp))
    delta_compression = 'C'
    output_csv = 'c'
    unit_of_time = 'm'
    host = 'http://{}.egaug.es/cgi-bin/egauge-show?'
    host = host.format(str(query_string)) + '&' + unit_of_time + '&' + output_csv + '&' + delta_compression
    time_window = {'t': api_start_timestamp, 'f': current_timestamp}
    request = requests.get(host, params=time_window)
    if request.status_code == requests.codes.ok:
        logging.info('[' + str(current_time) + '] ' + 'Data acquisition API request was successful for ' + query_string)
        readings = pandas.read_csv(StringIO(request.text))
        readings = readings.sort_values(by='Date & Time')
        # # Set header=False if we don't want to append header and set index=False to remove index column.
        # readings.to_csv(path_or_buf=output_file, index=False, header=False, mode='a+')
        # # readings.to_csv(path_or_buf=output_file, mode='a+')
        for purpose_sensor in purpose_sensors:
            error_log_row = orm_lonoa.ErrorLog(purpose_id=purpose_sensor.purpose_id, datetime=current_time, was_success=True, pipeline_stage=orm_lonoa.ErrorLog.PipelineStageEnum.data_acquisition)
            conn.add(error_log_row)
        conn.commit()
        return readings, purpose_sensors
    else:
        request.raise_for_status()


#def insert_egauge_readings_into_db(conn, readings, sensors):
def insert_readings_into_database(conn, readings, purpose_sensors):
    """
    1. iterate through purpose_sensors list
        2. iterate through rows in readings
            3. iterate through columns in row
                4. insert values where column name matches data_sensor_info_mapping
                5. keep track of last reading datetimes in new_last_updated_datetime
        6. attempt to update last_updated_datetime to new_last_updated_datetime using purpose_sensor.purpose_id if
        any rows were inserted
        7. generate timestamp of data insert attempt during step 2
        8. use purpose_sensor.purpose_id to insert success or failure of data insert attempt during step 2
    9. commit database inserts and updates
    """
    current_time = pendulum.now('Pacific/Honolulu')
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    rows_returned = readings.shape[0]
    for purpose_sensor in purpose_sensors:
        # The reading time of the last row inserted into the reading table
        rows_inserted = 0
        new_last_updated_datetime = ''
        # check if any values were returned
        if rows_returned > 0:
            # get a list of column names from readings dataframe
            columns = list(readings.columns.values)
            # attempt to insert data from each row of the readings dataframe into reading table
            for row in readings.itertuples():
                # appears that no timezone shifting needed but needs further testing
                row_datetime = pendulum.from_timestamp(row[1])  # in_timezone('Pacific/Honolulu')
                row_datetime = row_datetime.set(microsecond=row_datetime.microsecond - (row_datetime.microsecond % 10000))
                # iterate through each column after "Date & Time"
                for i, column_reading in enumerate(row[2:]):
                    row_reading = column_reading
                    # get column name
                    column_name = columns[i+1]
                    # only insert column's reading if data_sensor_info_mapping matches column_name
                    if purpose_sensor.data_sensor_info_mapping == column_name:
                        reading_row = orm_lonoa.Reading(purpose_id=purpose_sensor.purpose_id, datetime=row_datetime, reading=row_reading, units=purpose_sensor.unit, upload_timestamp=current_time)
                        conn.add(reading_row)
                        rows_inserted += 1
                        new_last_updated_datetime = row_datetime
        if rows_inserted > 0:
            conn.query(orm_lonoa.SensorInfo.purpose_id).filter(orm_lonoa.SensorInfo.purpose_id == purpose_sensor.purpose_id).update({"last_updated_datetime": new_last_updated_datetime})
        error_log_row = orm_lonoa.ErrorLog(purpose_id=purpose_sensor.purpose_id, datetime=current_time, pipeline_stage=orm_lonoa.ErrorLog.PipelineStageEnum.database_insertion, was_success=True)
        conn.add(error_log_row)
        # need to flush and refresh to get error_log_row.log_id
        conn.flush()
        conn.refresh(error_log_row)
        # update current set of readings with related log_id
        conn.query(orm_lonoa.Reading.log_id).\
            filter(orm_lonoa.Reading.purpose_id == purpose_sensor.purpose_id,
                   orm_lonoa.Reading.upload_timestamp == current_time).\
            update({'log_id':error_log_row.log_id})
        logging.info(str(rows_inserted) + ' readings(s) attempted to be inserted by ' + SCRIPT_NAME + ' for purpose id ' + str(purpose_sensor.purpose_id))
    conn.commit()


#log_failure_to_get_readings_from_egauge_api
def log_failure_to_connect_to_api(conn, exception, query_string):
    current_time = pendulum.now('Pacific/Honolulu')
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    # get all purpose_ids associated with query_string
    purpose_ids = [purpose_id[0] for purpose_id in conn.query(orm_lonoa.SensorInfo.purpose_id).filter_by(query_string=query_string, is_active=True)]
    logging.exception('Egauge API data request error')
    for purpose_id in purpose_ids:
        error_log_row = orm_lonoa.ErrorLog(datetime=current_time, error_type=exception.__class__.__name__, pipeline_stage=orm_lonoa.ErrorLog.PipelineStageEnum.data_acquisition, purpose_id=purpose_id, was_success=False)
        conn.add(error_log_row)
        conn.commit()


#log_failure_to_insert_egauge_readings_into_db
# need to continue testing if I should call conn.rollback() in this function
def log_failure_to_connect_to_database(conn, exception, purpose_sensors):
    current_time = pendulum.now('Pacific/Honolulu')
    current_time = current_time.set(microsecond=current_time.microsecond - (current_time.microsecond % 10000))
    logging.exception('Egauge reading insertion error')
    conn.rollback()
    for purpose_sensor in purpose_sensors:
        error_log_row = orm_lonoa.ErrorLog(datetime=current_time, error_type=exception.__class__.__name__, purpose_id=purpose_sensor.purpose_id, pipeline_stage=orm_lonoa.ErrorLog.PipelineStageEnum.database_insertion, was_success=False)
        conn.add(error_log_row)
        conn.commit()


if __name__ == '__main__':
    set_logging_settings()
    # start the database connection
    conn = get_db_handler()
    # get a list of all unique query_string's for active egauges from sensor_info table
    query_strings = [query_string[0] for query_string in conn.query(orm_lonoa.SensorInfo.query_string).filter_by(script_folder=orm_lonoa.SensorInfo.ScriptFolderEnum.egauge, is_active=True).distinct()]
    for query_string in query_strings:
        try:
            # readings is a pandas dataframe
            readings, purpose_sensors = get_data_from_api(conn, query_string)
        # catch egauge api request exceptions like requests.exceptions.ConnectionError, ValueError
        except (requests.exceptions.ConnectionError, Exception) as e:
            log_failure_to_connect_to_api(conn, e, query_string)
            continue
        try:
            insert_readings_into_database(conn, readings, purpose_sensors)
        # catch database errors like sqlalchemy.exc.InternalError, sqlalchemy.exc.OperationalError
        except Exception as e:
            log_failure_to_connect_to_database(conn, e, purpose_sensors)
    conn.close()
