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
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(df)
                #for to_csv set header=False if we don't want to append header and set index=False to remove index and prevent header prepending a comma
                df.to_csv(path_or_buf=output_file)
            #used to remove leading comma from column headers string
            df_columns = ''
            for value in df.columns.values:
                if(df_columns != ''):
                    df_columns = df_columns + value + ','
                else:
                    df_columns = value + ','
        else:
            r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
    #catch errors if any log files do not open successfully for writing
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
