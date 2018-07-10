"""
Test suite for egauge_api using the unittest module
"""

from freezegun import freeze_time

import arrow
import egauge_api
import filecmp
import os
import random
import unittest

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

class TestEgaugeAPI(unittest.TestCase):
    """
    A test suite for egauge_api

    Automatically runs any function starting with 'test_' in its name when main() is called

    Currently has tests for
        1. running pull_egauge_data() with no pre-existing timestamp file
        2. running pull_egauge_data() with a timestamp file that already has one timestamp

     BUGS:
      - setting current time using freezegun will result in any logged error messages using the 'frozen' time instead of the actual current time of the system.
      - running pull_egauge_data using freezegun prevents time elapsed from working properly
    """
    def test_blank_timestamp_file(self, sensor_id='725', unit_of_time='m'):
        START_TIME = arrow.get('2018-01-01T00:00:00.000-10:00').timestamp
        END_TIME = arrow.get('2018-01-01T01:00:00.000-10:00').timestamp
        self.assertTrue(START_TIME < END_TIME)

        TEST_OUTPUT = SCRIPT_DIRECTORY + '/test_output.log'
        TEST_TIMESTAMP_LOG = SCRIPT_DIRECTORY + '/test_timestamp.log'
        self.assertFalse(os.path.isfile(TEST_TIMESTAMP_LOG))

        with freeze_time(time_to_freeze=arrow.get(END_TIME).format('YYYY-MM-DD HH:mm:ss ZZ')):
            egauge_api.pull_egauge_data(sensor_id, unit_of_time, TEST_OUTPUT, TEST_TIMESTAMP_LOG)

        with open(TEST_TIMESTAMP_LOG, 'a+') as timestamp_file:
            timestamp_file.seek(0)
            for line in timestamp_file:
                line = line.rstrip()
                if line is not '':
                    latest_timestamp_read_from_file = int(line)
            self.assertTrue(latest_timestamp_read_from_file == END_TIME)
            self.assertFalse(os.path.isfile(TEST_OUTPUT))
        os.remove(TEST_TIMESTAMP_LOG)

    def test_pull_egauge_data(self):
        """
        Test running pull_egauge_data multiple times to confirm that there are no missing values and that there are no duplicate values

        Use freezegun to manually set the 'current time' for testing

        Call pull_egauge_data() over a large amount of time and output the data to a expected output file
        Call pull_egauge_data() multiple times adding up to that same amount of time and append data to a test output file
            Use a for loop to iterate through elapsed time with random variations that will be subtracted from the current time interval to account for time variation in testing
        Compare the expected and test files for differences

        """
        sensors = ['725']
        # sensors = ['725', '795', '31871']
        for sensor_id in sensors:
            #set START_TIME and END_TIME by converting a human-readable time into a unix timestamp
            START_TIME = arrow.get('2018-01-01T00:00:00.000-10:00').timestamp
            END_TIME = arrow.get('2018-01-01T04:01:03.000-10:00').timestamp

            self.assertTrue(START_TIME < END_TIME)

            unit_of_time = 'm'

            EXPECTED_OUTPUT = SCRIPT_DIRECTORY + '/expected_output.log'
            EXPECTED_TIMESTAMP_LOG = SCRIPT_DIRECTORY + '/expected_timestamp.log'
            #open EXPECTED_TIMESTAMP_LOG and append START_TIME
            with open(EXPECTED_TIMESTAMP_LOG, 'a+') as exp_test_file:
                exp_test_file.write(str(START_TIME) + '\n')

            #sensor_id, unit_of_time, output_file, timestamp_log
            with freeze_time(time_to_freeze=arrow.get(END_TIME).format('YYYY-MM-DD HH:mm:ss ZZ')):
                egauge_api.pull_egauge_data(sensor_id, unit_of_time, EXPECTED_OUTPUT, EXPECTED_TIMESTAMP_LOG)

            #notice that START_TIME is used to set current_timestamp because the time interval will be added within the while loop
            TEST_OUTPUT = SCRIPT_DIRECTORY + '/test_output.log'
            TEST_TIMESTAMP_LOG = SCRIPT_DIRECTORY + '/test_timestamp.log'
            #open TEST_TIMESTAMP_LOG and append START_TIME
            with open(TEST_TIMESTAMP_LOG, 'a+') as test_file:
                test_file.write(str(START_TIME) + '\n')

            # MAX_TIME_INTERVAL represents the maximum number of seconds elapsed between calls
            MAX_TIME_INTERVAL = 3600
            # seed can be any integer; setting the seed allows for consistency in testing
            random.seed(42)
            # use floor division to ensure that an int is returned from dividing an int by an int
            MAX_NUMBER_OF_PULLS = int((END_TIME - START_TIME)//MAX_TIME_INTERVAL)
            # use for loop to simulate calling egauge_api.pull_egauge_data() multiple times over randomly generated periods of time
            for number_of_pulls in range(MAX_NUMBER_OF_PULLS + 1):
                current_timestamp = ''
                if(number_of_pulls < MAX_NUMBER_OF_PULLS):
                    max_time_elapsed = (number_of_pulls + 1) * MAX_TIME_INTERVAL
                    random_time_variance = random.randrange(1, MAX_TIME_INTERVAL)
                    current_timestamp = max_time_elapsed - random_time_variance + START_TIME
                else: #during the last pull, set the current time to END_TIME
                    current_timestamp = END_TIME
                # make a call to pull_egauge_data() setting current time to the latest value of current_timestamp
                with freeze_time(time_to_freeze=arrow.get(current_timestamp).format('YYYY-MM-DD HH:mm:ss ZZ')):
                    egauge_api.pull_egauge_data(sensor_id, unit_of_time, TEST_OUTPUT, TEST_TIMESTAMP_LOG)

            #confirm that the output files match
            self.assertTrue(filecmp.cmp(EXPECTED_OUTPUT, TEST_OUTPUT))

            #cleanup
            os.remove(EXPECTED_TIMESTAMP_LOG)
            os.remove(TEST_TIMESTAMP_LOG)
            os.remove(EXPECTED_OUTPUT)
            os.remove(TEST_OUTPUT)

if __name__ == '__main__':
    unittest.main()
