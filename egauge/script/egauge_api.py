'''
This script will use the egauge api to get the data as a csv from the interval of time between the two timestamps and append that csv data (without the headers) to the output file path
'''

from io import StringIO

import os
import pandas as pd
import requests
import sys
import traceback

def main():
    #egauge_request('1526548513', '1526549515', '725', '~/Projects/egauge/output.csv')\

    #originally the start of egauge_request(start_timestamp, end_timestamp, sensor_id, output_file)
    script, start_timestamp, end_timestamp, sensor_id, output_file = sys.argv

    minutes='m'
    output_csv='c'
    delta_compression='C'
    #originally a call to set_egauge_host(sensor_id, minutes='m', output_csv='c', delta_compression='C'):
    host = 'http://egauge{}.egaug.es/cgi-bin/egauge-show?'
    host = host.format(sensor_id) + '&' + minutes + '&' + output_csv + '&' + delta_compression

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
                df.to_csv(path_or_buf = output_file)

            #df_columns = convert_list_to_csv_row(df.columns.values)
            df_columns = ''
            #originally a call to convert_list_to_csv_row(values)
            for value in df.columns.values:
                if(df_columns != ''):
                    df_columns = df_columns + value + ','
                else:
                    df_columns = value + ','
        else:
            r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)

if __name__ == "__main__":
    main()
