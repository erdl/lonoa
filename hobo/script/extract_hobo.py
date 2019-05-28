#!../../egauge/script/env/bin/python3
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import configparser
import csv
import glob
import logging
import orm_hobo
import os
import pandas
import pendulum


logging.basicConfig(filename='error.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def get_db_handler():
    """
    connect to database by creating a session
    """
    config_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent) + "/config.txt"
    with open(config_path, "r") as file:
        # prepend '[DEFAULT]\n' since ConfigParser requires section headers in config files
        config_string = '[DEFAULT]\n' + file.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    db_url = "postgresql:///" + config['DEFAULT']['db']
    # connect to the database
    db = create_engine(db_url)
    Session = sessionmaker(db)
    conn = Session()
    return conn


def get_csv_from_folder_not_in_db(conn, csv_filename):
    """
    Create reading dataframe and metadata list using csv file

    Takes database session 'conn' and 'csv_filename' string as arguments

    Opens csv file, reads file as dataframe and extracts metadata into a list
    Checks if the timestamp of the earliest and latest rows in dataframe are already in db for a given sensor_id
    """
    current_time = pendulum.now('Pacific/Honolulu')
    #assume there are no new readings by default
    new_readings = False
    with open(csv_filename, 'r') as file:
        reader = csv.reader(file)
        # Remove the first row, which breaks the csv format and contains the hobo sensor id
        line1 = next(reader)
        line1 = line1[0]
        #Extract sensor_id
        # the next commented out line has a weird bug that sometimes removes the last digit instead of the trailing quotation mark
        # sensor_id = line1.split(': ')[1][0:-1]
        sensor_id = line1.split(': ')[1][0:]
        # check if trailing quotation mark is present and remove if so
        if sensor_id[-1:] is "\"":
            sensor_id = sensor_id[0:-1]
        #Store in table the remainder of the table
        table = list(reader)
    # #TEST
    # print(table[0:3])
    # create dataframe from table
    csv_readings = pandas.DataFrame(table[1:], columns=table[0])
    # remove 1st column from dataframe ("#"), since created dataframe automatically has its own index column
    csv_readings = csv_readings.iloc[:, 1:]
    # #Extract timezone and units
    # timezone_units = csv_readings.columns
    # print("timezone_units: ", timezone_units)
    # #First separate the variable name from the timezone/unit description
    # names = [x.split(', ')[0] for x in timezone_units] # should look like ['Date Time', 'Temp', 'RH', 'Intensity']
    # # # get a list of data_sensor_info_mappings by splitting timezone_units
    # # data_sensor_info_mappings = [x.split(' (')[0] for x in timezone_units[1:]] # should look like "['Temp, °F', 'RH, %', 'Intensity, lum/ft²']"
    # csv_readings.columns = names #alternate # [names[0]] + data_sensor_info_mappings
    # create a list of sensor_info_rows which will be used to iterate through each data_sensor_info_mapping in each csv_reading row in the insert...() function
    sensor_info_rows = []
    for data_sensor_info_mapping in csv_readings.columns[1:]:
        purpose_id, last_updated_datetime, units = conn.query(orm_hobo.SensorInfo.purpose_id, orm_hobo.SensorInfo.last_updated_datetime, orm_hobo.SensorInfo.units).filter_by(sensor_id=sensor_id, data_sensor_info_mapping=data_sensor_info_mapping, is_active=True).first()[:3]
        sensor_info_rows.append(orm_hobo.SensorInfo(data_sensor_info_mapping=data_sensor_info_mapping, purpose_id=purpose_id, last_updated_datetime=last_updated_datetime, units=units))
    # # Units
    # timezone_units = [x.split(', ')[1] for x in timezone_units]
    # #Timezone needs no further pre-processing
    # timezone = timezone_units[0]
    # #But units do:
    # units = [x.split(' ')[0] for x in timezone_units[1:]]
    #Remove duplicates
    csv_readings = csv_readings.drop_duplicates(subset=['Date Time, GMT-10:00'])
    #convert date column from string objects to datetimes
    csv_readings['Date Time, GMT-10:00'] = pandas.to_datetime(csv_readings['Date Time, GMT-10:00'])
    #sort csv_readings dataframe by timestamp
    csv_readings = csv_readings.sort_values(by=['Date Time, GMT-10:00'])
    # #TEST
    # csv_readings.to_csv(path_or_buf='output.txt')
    csv_modified_timestamp = pendulum.from_timestamp(os.path.getmtime(csv_filename), tz='Pacific/Honolulu')
    earliest_csv_timestamp = pendulum.instance(csv_readings.iloc[0]['Date Time, GMT-10:00'], 'Pacific/Honolulu')
    latest_csv_timestamp = pendulum.instance(csv_readings.iloc[csv_readings.shape[0]-1]['Date Time, GMT-10:00'], 'Pacific/Honolulu')
    for sensor_info_row in sensor_info_rows:
        error_log_row = orm_hobo.ErrorLog(status=True, purpose_id=sensor_info_row.purpose_id, datetime=current_time, pipeline_stage=orm_hobo.ErrorLog.PipelineStageEnum.data_acquisition)
        conn.add(error_log_row)
        # need to flush and refresh to get error_log_row.log_id
        conn.flush()
        conn.refresh(error_log_row)
        csv_filename_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="csv_filename", information_value=csv_filename)
        conn.add(csv_filename_row)
        csv_modified_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="csv_modified_timestamp", information_value=csv_modified_timestamp)
        conn.add(csv_modified_timestamp_row)
        earliest_csv_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="earliest_csv_timestamp", information_value=earliest_csv_timestamp)
        conn.add(earliest_csv_timestamp_row)
        latest_csv_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="latest_csv_timestamp", information_value=latest_csv_timestamp)
        conn.add(latest_csv_timestamp_row)
    # check if earliest and latest file_timestamps are already in db and set new_readings variable
    # assume that if first or last timestamps in csv were already inserted for that given timestamp and sensor_id, then all were already inserted
    earliest_csv_timestamp_is_in_db = conn.query(orm_hobo.Readings).filter_by(datetime=earliest_csv_timestamp, purpose_id=sensor_info_rows[0].purpose_id).first()
    latest_csv_timestamp_is_in_db = conn.query(orm_hobo.Readings).filter_by(datetime=latest_csv_timestamp, purpose_id=sensor_info_rows[0].purpose_id).first()
    if not earliest_csv_timestamp_is_in_db and not latest_csv_timestamp_is_in_db:
        new_readings = True
    return csv_readings, (new_readings, earliest_csv_timestamp, csv_modified_timestamp, sensor_id, latest_csv_timestamp, sensor_info_rows)


def insert_csv_readings_into_db(conn, csv_readings, csv_metadata, csv_filename):
    """
    Parse rows in csv_readings dataframe into readings table rows and insert

    Check csv_readings dataframe was set and that it has at least one row

    Use csv_metadata
    """
    current_time = pendulum.now('Pacific/Honolulu')
    #useful if main does not use continue
    #check if csv_readings was initialized as a dataframe
    if isinstance(csv_readings, pandas.DataFrame):
        if csv_readings.empty:
            return
        else:
            print('readings extracted from csv')
    #executes if not initialized as a dataframe
    elif not csv_readings:
        logging.exception('csv_readings set to None')
        return
    new_readings, earliest_csv_timestamp, csv_modified_timestamp, sensor_id, latest_csv_timestamp, sensor_info_rows = csv_metadata
    if not new_readings:
        raise Exception("csv readings already inserted")
    rows_returned = csv_readings.shape[0]
    if rows_returned > 0:
        for csv_reading in csv_readings.itertuples():
            for i in range(0, len(sensor_info_rows)):
                reading_row = orm_hobo.Readings(datetime=csv_reading[1], purpose_id=sensor_info_rows[i].purpose_id, value=csv_reading[i+2], units=sensor_info_rows[i].units)
                conn.add(reading_row)
            last_reading_row_datetime = csv_reading[1]
    #update last_updated_datetime column for relevant rows in sensor_info table
    for sensor_info_row in sensor_info_rows:
        # account for if csv files uploaded out of order by checking if last_reading_row_datetime is later than last_updated_datetime
        if not sensor_info_row.last_updated_datetime or sensor_info_row.last_updated_datetime < last_reading_row_datetime:
            conn.query(orm_hobo.SensorInfo.purpose_id).filter(orm_hobo.SensorInfo.purpose_id == sensor_info_row.purpose_id).update({"last_updated_datetime": last_reading_row_datetime})
        error_log_row = orm_hobo.ErrorLog(status=True, purpose_id=sensor_info_row.purpose_id, datetime=current_time, pipeline_stage=orm_hobo.ErrorLog.PipelineStageEnum.database_insertion)
        conn.add(error_log_row)
        # need to flush and refresh to get error_log_row.log_id
        conn.flush()
        conn.refresh(error_log_row)
        csv_filename_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="csv_filename", information_value=csv_filename)
        conn.add(csv_filename_row)
        csv_modified_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="csv_modified_timestamp", information_value=csv_modified_timestamp)
        conn.add(csv_modified_timestamp_row)
        earliest_csv_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="earliest_csv_timestamp", information_value=earliest_csv_timestamp)
        conn.add(earliest_csv_timestamp_row)
        latest_csv_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="latest_csv_timestamp", information_value=latest_csv_timestamp)
        conn.add(latest_csv_timestamp_row)
    conn.commit()


def log_failure_to_get_csv_readings_from_folder_not_in_db(conn, csv_filename, exception):
    current_time = pendulum.now('Pacific/Honolulu')
    logging.exception('log_failure_to_get_csv_readings_from_folder_not_in_db')
    error_log_row = orm_hobo.ErrorLog(status=False, datetime=current_time, error_type=exception.__class__.__name__, pipeline_stage=orm_hobo.ErrorLog.PipelineStageEnum.data_acquisition)
    conn.add(error_log_row)
    # need to flush and refresh to get error_log_row.log_id
    conn.flush()
    conn.refresh(error_log_row)
    csv_filename_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="csv_filename", information_value=csv_filename)
    conn.add(csv_filename_row)
    conn.commit()


def log_failure_to_insert_csv_readings_into_db(conn, csv_filename, csv_metadata, exception):
    current_time = pendulum.now('Pacific/Honolulu')
    new_readings, earliest_csv_timestamp, csv_modified_timestamp, sensor_id, latest_csv_timestamp, sensor_info_rows = csv_metadata
    #rollback any reading insertions during that iteration of for loop in main
    conn.rollback()
    logging.exception('log_failure_to_insert_csv_readings_into_db')
    for sensor_info_row in sensor_info_rows:
        # set status to "" if readings were already inserted
        if not new_readings:
            error_log_row = orm_hobo.ErrorLog(purpose_id=sensor_info_row.purpose_id, datetime=current_time, error_type=exception.__class__.__name__,pipeline_stage=orm_hobo.ErrorLog.PipelineStageEnum.database_insertion)
        # set status to False if readings were new but an error was thrown
        else:
            error_log_row = orm_hobo.ErrorLog(purpose_id=sensor_info_row.purpose_id, status=False, datetime=current_time, error_type=exception.__class__.__name__,  pipeline_stage=orm_hobo.ErrorLog.PipelineStageEnum.database_insertion)
        conn.add(error_log_row)
        # need to flush and refresh to get error_log_row.log_id
        conn.flush()
        conn.refresh(error_log_row)
        csv_filename_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="csv_filename", information_value=csv_filename)
        conn.add(csv_filename_row)
        csv_modified_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="csv_modified_timestamp", information_value=csv_modified_timestamp)
        conn.add(csv_modified_timestamp_row)
        earliest_csv_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="earliest_csv_timestamp", information_value=earliest_csv_timestamp)
        conn.add(earliest_csv_timestamp_row)
        latest_csv_timestamp_row = orm_hobo.ErrorLogDetails(log_id=error_log_row.log_id, information_type="latest_csv_timestamp", information_value=latest_csv_timestamp)
        conn.add(latest_csv_timestamp_row)
    conn.commit()


if __name__=='__main__':
    conn = get_db_handler()
    csv_filenames = glob.glob('./to-insert/*.csv')
    for csv_filename in csv_filenames:
        try:
             csv_readings, csv_metadata = get_csv_from_folder_not_in_db(conn, csv_filename)
        except Exception as exception:
             log_failure_to_get_csv_readings_from_folder_not_in_db(conn, csv_filename, exception)
             continue
        try:
             insert_csv_readings_into_db(conn, csv_readings, csv_metadata, csv_filename)
        except Exception as exception:
             log_failure_to_insert_csv_readings_into_db(conn, csv_filename, csv_metadata, exception)
