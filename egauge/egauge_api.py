'''
This script will use the egauge api to get the data as a csv from the interval of time between the two timestamps and append that csv data (without the headers) to the output file path
'''

from io import StringIO

import os
import pandas as pd
import requests
import sys
import traceback

def egauge_request(start_timestamp, end_timestamp, sensor_id, output_file):
    host = set_egauge_host(sensor_id)
    time_window = {'t': start_timestamp, 'f': end_timestamp}
    try:
        r = requests.get(host,params=time_window)
        if(r.status_code == requests.codes.ok):
            print('Request was successful', str(r))
            df = pd.read_csv(StringIO(r.text))
            '''with open(request_dict['csv_output_path'], 'a' ) as f:
                #set header=False if we don't want to append header
                #set index=False to prevent header prepending a comma
                df.to_csv(f, sep=',', header=False, index=False)'''
            with pd.option_context('display.max_rows', None, 'display.max_columns', 4):
                print(df)
            df_columns = convert_list_to_csv_row(df.columns.values)
        else:
            r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)

def main():
    egauge_request('1526548513', '1526549515', '725', '~/Projects/egauge/output.csv');

#takes a list and returns a string in csv format
def convert_list_to_csv_row(values):
    csv_row = ''
    for value in values:
        if(csv_row != ''):
            csv_row = csv_row + value + ','
        else:
            csv_row = value + ','
    return csv_row

#print each value in sys.argv
def print_args():
    for arg in sys.argv:
        print ('arg is ' + arg)

# set host for egauge api get request
def set_egauge_host(sensor_id, minutes='m', output_csv='c', delta_compression='C'):
    host = 'http://egauge{}.egaug.es/cgi-bin/egauge-show?'
    host = host.format(sensor_id) + '&' \
    + minutes + '&' \
    + output_csv + '&' \
    + delta_compression
    return host

if __name__ == "__main__":
    script, start, end, egauge_id, file_path = sys.argv

    egauge_request(start, end, egauge_id, file_path)
