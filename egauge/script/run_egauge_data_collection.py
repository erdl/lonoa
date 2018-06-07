'''
This script will read the latest Linux timestamp from a file and make a call to egauge_api.py using the read timestamp as the start time and the current time as the end time.
'''

import egauge_api

if __name__ == "__main__":
    #egauge_api.egauge_request('1526548513', '1526549515', '725', '~/Projects/egauge/output.csv');
