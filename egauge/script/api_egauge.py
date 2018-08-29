#!./env/bin/python3
"""
This script makes egauge api requests using data retrieved from a database

You can run this script using the form:
python3 api_egauge.py <sensor id> <database url> <unit of time>

Example command: python3 api_egauge.py 725 postgresql:///egauge m
"""

from io import StringIO

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func #used for sql max() function

import arrow
import logging
import orm_egauge
import os
import pandas
import requests
#import sqlalchemy #used for errors like sqlalchemy.exc.InternalError, sqlalchemy.exc.OperationalError
import sys
import traceback


#SCRIPT_NAME = os.path.basename(__file__) # will be used for future process lock
TIME_GRANULARITY_IN_SECONDS = 60
logging.basicConfig(filename='error.log',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


# connect to database by creating a session
def get_db_handler(db_url):
    # connect to the database
    db = create_engine(db_url)
    Session = sessionmaker(db)
    conn = Session()
    return conn


# insert row into database insertion timestamp and close database connection
# is_success represents if rows were successfully inserted into reading
def insert_timestamp_and_close_db_connection(conn, is_success, insertion_time):
    #roll back all changes to database if no rows of readings successfully obtained and inserted
    if not is_success:
        conn.rollback()
    timestamp_row = orm_egauge.DatabaseInsertionTimestamp(timestamp=insertion_time.datetime, is_success=is_success)
    conn.add(timestamp_row)
    conn.commit()
    conn.close()


# will need to update once relating each database_insertion_time to egauge sensor is decided (add filter for sensor id)
# Obtains the greatest 'success' timestamp in database_insertion_timestamp
# which should be the the same timestamp for the last reading successfully inserted into Reading
def get_most_recent_timestamp_from_db(conn):
    last_reading_time = ''

    # conn.query(func.max...)[0][0] returns the first element in the first tuple in a list
    latest_datetime_successfully_inserted = conn.query(func.max(orm_egauge.DatabaseInsertionTimestamp.timestamp)).filter_by(is_success=True)[0][0]

    if latest_datetime_successfully_inserted:
        # shift timestamp 10 hours forward since HST is GMT - 10 hours
        last_reading_time = arrow.get(latest_datetime_successfully_inserted).shift(hours = +10)

    return last_reading_time


# returns a readings dataframe
def get_data_from_api(api_start_time, api_end_time, sensor_id, unit_of_time):
    # add time granularity (60 seconds by default) to api_start_timestamp because we want to record last inserted time time database_insertion_timestamp and\
    # the egauge api returns values inclusive of the start time and exclusive of the end time
    api_start_timestamp = api_start_time.timestamp + TIME_GRANULARITY_IN_SECONDS
    # The range returned is exclusive of the api end timestamp; eg. all data collected by the egauge sensor from the start time up to but not including the end time will be returned
    api_end_timestamp = api_end_time.timestamp
    if api_start_timestamp > api_end_timestamp:
        raise ValueError('Error: api_start_timestamp ' + str(arrow.get(api_start_timestamp)) + ' was later than api_end_timestamp ' + str(arrow.get(api_end_timestamp)))
    output_csv = 'c'
    delta_compression = 'C'
    host = 'http://egauge{}.egaug.es/cgi-bin/egauge-show?'
    host = host.format(str(sensor_id)) + '&' + unit_of_time + '&' + output_csv + '&' + delta_compression
    time_window = {'t': api_start_timestamp, 'f': api_end_timestamp}
    request = requests.get(host, params=time_window)

    if request.status_code == requests.codes.ok:
        print('[' + str(arrow.get(api_end_timestamp)) + '] ' + 'Request was successful' + str(request))
        readings = pandas.read_csv(StringIO(request.text))
        readings = readings.sort_values(by='Date & Time')
        # # Set header=False if we don't want to append header and set index=False to remove index column.
        # readings.to_csv(path_or_buf=output_file, index=False, header=False, mode='a+')
        # # readings.to_csv(path_or_buf=output_file, mode='a+')
        return readings
    else:
        request.raise_for_status()


# returns database insertion time and True if rows of readings were inserted OR
# arrow.now() and False if no readings were inserted
def insert_readings_into_database(conn, readings, sensor_id):
    database_insertion_time = ''
    is_success = False
    rows_returned = readings.shape[0]
    # check if any values were returned
    if rows_returned > 0:
        row_insertion_time = arrow.now()
        # get a list of column names from readings dataframe
        columns = list(readings.columns.values)
        # attempt to insert data from each row of the readings dataframe into reading table
        for row in readings.itertuples():
            row_datetime = arrow.get(row[1]).datetime
            for i, column_reading in enumerate(row[2:]):
                #TEST
                # print('i: ', i, ', column_reading: ',column_reading, 'columns[i+1]: ', columns[i+1])
                row_reading = column_reading
                row_units = columns[i+1] # insert column name at index 1 for prototype
                # the upload timestamp for all rows in the readings dataframe will use the same value (current_time) which was set at the beginning of pull_egauge_data()
                reading_row = orm_egauge.Reading(sensor_id=sensor_id, timestamp=row_datetime, units=row_units, reading=row_reading, upload_timestamp=row_insertion_time.datetime)
                conn.add(reading_row)
                database_insertion_time = arrow.get(row_datetime)
    print(str(rows_returned) + ' row(s) returned by egauge api in ', end='')

    if database_insertion_time:
        is_success = True
    else:
        database_insertion_time = arrow.now()
    return database_insertion_time, is_success


def main(sensor_id='31871', db_url='postgresql:///egauge', unit_of_time='m'):
    """
    This function pulls egauge sensor data.

    Data pulled will start at and include the time read from the timestamp log up to (but not including) the current time. The data (not including the headers) pulled from the sensors by this program will be appended to a csv file ('output.log' by default).
    Any exceptions thrown during execution will be logged to a file.

    Keyword arguments:
        sensor_id: a string representing the id of the egauge sensor
        db_url: the host used to connect to a specific postgresql db
        unit_of_time: the unit of time we want each reading returned over (per minute, per hour, etc)
    """
    # cast sensor_id as int for consistency since sensor_id in db may be int
    sensor_id = int(sensor_id)
    # start the database connection
    conn = get_db_handler(db_url)

    last_reading_time = get_most_recent_timestamp_from_db(conn)
    # if no timestamp is found, insert the current time and skip egauge api request, etc.
    # REMEMBER if script is used with an empty DatabaseInsertionTimestamp table, the first run will insert\
    # current_time into the database_insertion_timestamp by default, BUT values associated with that timestamp will
    # NOT be inserted
    if not last_reading_time:
        insert_timestamp_and_close_db_connection(conn, True, arrow.now())
    else:
        # tracks how long the api request and insertion takes
        request_timer_start = arrow.now()

        try:
            # readings is a pandas dataframe
            readings = get_data_from_api(last_reading_time, arrow.now(), sensor_id, unit_of_time)
        # catch egauge api request exceptions like requests.exceptions.ConnectionError, ValueError
        except (requests.exceptions.ConnectionError, Exception) as e:
            logging.exception('API data request error')
            insert_timestamp_and_close_db_connection(conn, False, arrow.now())
            sys.exit()

        try:
            database_insertion_time, is_success = insert_readings_into_database(conn, readings, sensor_id)
            insert_timestamp_and_close_db_connection(conn, is_success, database_insertion_time)
        # catch database errors like sqlalchemy.exc.InternalError, sqlalchemy.exc.OperationalError
        except Exception as e:
            logging.exception('Database insertion error')
            insert_timestamp_and_close_db_connection(conn, False, arrow.now())
            sys.exit()

        request_timer_end = arrow.now()
        request_time_elapsed = request_timer_end - request_timer_start
        print(str(request_time_elapsed) + ' seconds')


if __name__ == "__main__":
    # slice off script name argument since it is unused
    try:
        main(*sys.argv[1:])
    # catch and log to file any weird errors that would otherwise not have been caught
    except Exception as e:
        logging.exception('This error was caught outside of main')
