#!./env/bin/python3
"""
Test suite for api_egauge using the unittest module

Requires access to postgresql databases: 'expected' and 'test'.
MAKE SURE THAT THOSE DATABASES ARE NOT ALREADY BEING USED
BEFORE RUNNING UNIT TESTS, SINCE THEY WILL BE MODIFIED DURING TESTING
"""

from freezegun import freeze_time

import arrow
import api_egauge
import filecmp
import orm_egauge
import os
import random
import unittest

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
EXPECTED_DATABASE_URL = 'postgresql:///expected'
TEST_DATABASE_URL = 'postgresql:///test'

# EXPECTED_OUTPUT = SCRIPT_DIRECTORY + '/expected_output.log'
# TEST_OUTPUT = SCRIPT_DIRECTORY + '/test_output.log'

EXPECTED_DUMP = 'expected_reading_dump.csv'
TEST_DUMP = 'test_reading_dump.csv'

SENSOR_IDS = ['31871']
UNIT_OF_TIME = 'm'

START_TIME = arrow.get('2018-01-01T00:00:00.000-10:00')
END_TIME = arrow.get('2018-01-01T04:00:00.000-10:00')

class TestEgaugeAPI(unittest.TestCase):
    """
    A test suite for api_egauge

    Automatically runs any function starting with 'test_' in its name when main() is called
    Automatically runs setUp() before each test function runs and tearDown() after each 'test'
    function runs

    Currently has tests running main()

    BUGS:
    - setting current time using freezegun will result in any logged error messages using the 'frozen' time instead of the actual current time of the system.
    - running main using freezegun prevents time elapsed from working properly
    """

    def setUp(self):
        orm_egauge.setup(EXPECTED_DATABASE_URL)
        orm_egauge.setup(TEST_DATABASE_URL)

        freeze_start_time = START_TIME.format('YYYY-MM-DD HH:mm:ss ZZ')

        # initialize both databases' database_insertion_timestamp tables with the start time
        for sensor_id in SENSOR_IDS:
            with freeze_time(time_to_freeze=freeze_start_time):
                api_egauge.main(sensor_id, EXPECTED_DATABASE_URL)
            with freeze_time(time_to_freeze=freeze_start_time):
                api_egauge.main(sensor_id, TEST_DATABASE_URL)

    def tearDown(self):
        # os.remove(EXPECTED_OUTPUT)
        # os.remove(TEST_OUTPUT)
        orm_egauge.teardown(EXPECTED_DATABASE_URL)
        orm_egauge.teardown(TEST_DATABASE_URL)
        os.remove(EXPECTED_DUMP)
        os.remove(TEST_DUMP)

    def test_main(self):
        """
        Test running main multiple times to confirm that there are no missing values and that there are no duplicate values

        Use freezegun to manually set the 'current time' for testing

        Call main() over a large amount of time
        Call main() multiple times adding up to that same amount of time
        Dump the expected 'reading' table to csv and the test 'reading' table to
        another csv then compare the files to make sure that they match
        """

        for sensor_id in SENSOR_IDS:
            self.assertTrue(START_TIME < END_TIME)

            with freeze_time(time_to_freeze=END_TIME.format('YYYY-MM-DD HH:mm:ss ZZ')):
                api_egauge.main(sensor_id, EXPECTED_DATABASE_URL, UNIT_OF_TIME)

            # MAX_TIME_INTERVAL represents the maximum number of seconds elapsed between calls
            MAX_TIME_INTERVAL = 3600
            # seed can be any integer; setting the seed allows for consistency in testing
            random.seed(42)
            # use floor division to ensure that an int is returned from dividing an int by an int
            MAX_NUMBER_OF_PULLS = int((END_TIME.timestamp - START_TIME.timestamp)//MAX_TIME_INTERVAL)
            # use for loop to simulate calling api_egauge.main() multiple times over randomly generated periods of time
            for number_of_pulls in range(MAX_NUMBER_OF_PULLS + 1):
                current_timestamp = ''
                if(number_of_pulls < MAX_NUMBER_OF_PULLS):
                    max_time_elapsed = (number_of_pulls + 1) * MAX_TIME_INTERVAL
                    random_time_variance = random.randrange(1, MAX_TIME_INTERVAL)
                    current_timestamp = max_time_elapsed - random_time_variance + START_TIME.timestamp
                else:  # during the last pull, set the current time to END_TIME
                    current_timestamp = END_TIME.timestamp
                # make a call to main() setting current time to the latest value of current_timestamp
                with freeze_time(time_to_freeze=arrow.get(current_timestamp).format('YYYY-MM-DD HH:mm:ss ZZ')):
                    api_egauge.main(sensor_id, TEST_DATABASE_URL, UNIT_OF_TIME)

            orm_egauge.export_reading_to_csv(EXPECTED_DATABASE_URL, EXPECTED_DUMP)
            orm_egauge.export_reading_to_csv(TEST_DATABASE_URL, TEST_DUMP)

            # confirm that the output files match
            self.assertTrue(filecmp.cmp(EXPECTED_DUMP, TEST_DUMP))

if __name__ == '__main__':
    unittest.main()
