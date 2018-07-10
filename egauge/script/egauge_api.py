#!./env/bin/python3
"""
This script uses a timestamp file to keep track of and make egauge api requests for egauge sensor data.

Example command: python3 egauge_api.py 725 m ./output.log ./timestamp.log
"""

from io import StringIO

import arrow
import os
import pandas as pd
import requests
import sys
import traceback

script_name = os.path.basename(__file__)
error_log = 'error.log'
#a dictionary that maps unit_of_time arguments to the number of seconds in that unit
times = {
'm':60,
'h':3600
}

def pull_egauge_data(sensor_id='31871', unit_of_time='m', output_file='./output.log', timestamp_log='./timestamp.log'):
    """
    This function pulls egauge sensor data.

    Data pulled will start at and include the time read from the timestamp log up to (but not including) the current time. The data (not including the headers) pulled from the sensors by this program will be appended to a csv file ('output.log' by default).
    Any exceptions thrown during execution will be logged to a file.

    Keyword arguments:
        sensor_id: a string representing the id of the egauge sensor
        unit_of_time: the unit of time we want the data returned as
        output_file: the name of the file that egauge sensor data will be appended to
        timestamp_log: the name of the file that a timestamp will be read from and written to
    """
    try:
        current_timestamp = int(arrow.now().timestamp)
        # round down to the nearest unit of time (minute)
        current_timestamp = current_timestamp - (current_timestamp % times[unit_of_time])

        latest_timestamp_read_from_file = ''
        with open(timestamp_log, 'a+') as timestamp_file:
            timestamp_file.seek(0)
            for line in timestamp_file:
                line = line.rstrip()
                if line is not '':
                    latest_timestamp_read_from_file = int(line)

        if not latest_timestamp_read_from_file:
            with open(timestamp_log, 'a+') as timestamp_file:
                timestamp_file.write(str(current_timestamp) + '\n')
                print('File ' + timestamp_log + ' was empty. Appended current timestamp to file.')
        else:
            api_start_timestamp = latest_timestamp_read_from_file
            #The range returned is exclusive of the api end timestamp; eg. all data collected by the egauge sensor from the start time up to but not including the end time will be returned
            api_end_timestamp = current_timestamp
            if api_start_timestamp > api_end_timestamp:
                raise ValueError('Error: api_start_timestamp ' + str(arrow.get(api_start_timestamp)) + ' was later than api_end_timestamp '  + str(arrow.get(api_end_timestamp)))
            output_csv='c'
            delta_compression='C'
            host = 'http://egauge{}.egaug.es/cgi-bin/egauge-show?'
            host = host.format(sensor_id) + '&' + unit_of_time + '&' + output_csv + '&' + delta_compression
            time_window = {'t': api_start_timestamp, 'f': api_end_timestamp}

            request_timer_start = arrow.now()

            r = requests.get(host,params=time_window)
            if(r.status_code == requests.codes.ok):
                print('[' + str(arrow.get(current_timestamp)) + '] ' + 'Request was successful' + str(r))
                df = pd.read_csv(StringIO(r.text))
                df = df.sort_values(by='Date & Time')
                #Set header=False if we don't want to append header and set index=False to remove index column.
                df.to_csv(path_or_buf=output_file, index=False, header=False, mode='a+')
                rows_returned = df.shape[0]
                #check if any values were returned
                if rows_returned > 0:
                    #Will implement database insertion here
                    #Write current_timestamp to timestamp log
                    with open(timestamp_log, 'a+') as timestamp_file:
                        timestamp_file.write(str(current_timestamp) + '\n')
                request_timer_end = arrow.now()
                request_time_elapsed = request_timer_end - request_timer_start
                print(str(rows_returned) + ' row(s) returned by egauge api in ' + str(request_time_elapsed))
            else:
                r.raise_for_status()
    except Exception as e:
        error_msg = str(traceback.format_exc())
        print(error_msg)
        with open(error_log, 'a+') as error_file:
            current_time = arrow.now().format('ddd MMM DD YYYY HH:mm:ss ZZ')
            error_file.write('[' + str(current_time) + '] ')
            error_file.write(error_msg + '\n')

if __name__ == "__main__":
    #slice off script name argument since it is unused
    pull_egauge_data(*sys.argv[1:])
