#!./env/bin/python3
"""
Test suite for api_egauge using the unittest module

WARNING: running this test modifies the postgresql database named "test"
"""
from freezegun import freeze_time

import api_egauge
import orm_egauge
import pandas
import pendulum
import unittest


class TestEgaugeAPI(unittest.TestCase):
    """
    A test suite for api_egauge

    Automatically runs any function starting with 'test_' in its name when main() is called
    Automatically runs setUp() before and tearDown() after each of the 'test' functions run

    Currently has tests for get_data_from_api()
    """
    sensor_id = 'egauge791'
    db_url = 'postgresql:///test'


    def setUp(self):
        db = api_egauge.create_engine(self.db_url)
        orm_egauge.BASE.metadata.create_all(db)


    def tearDown(self):
        db = api_egauge.create_engine(self.db_url)
        orm_egauge.BASE.metadata.drop_all(db)


    # test if two subsequent calls to get_data_from_api() will return duplicate timestamps
    def test_api_requested_data_doesnt_overlap(self):
        db = api_egauge.create_engine(self.db_url)
        Session = api_egauge.sessionmaker(db)
        conn = Session()
        timestamps = [pendulum.parse('2019-02-01T00:00:00-10:00'), pendulum.parse('2019-02-01T00:05:00-10:00'), pendulum.parse('2019-02-01T00:10:00-10:00')]
        # Shift timestamp back by 60 seconds when inserting table
        # because get_data_from_api() will use timestamp + 60 seconds
        # for the start time in its api request.
        sensor_row = orm_egauge.SensorInfo(sensor_id=self.sensor_id, sensor_type="egauge", purpose_id=1, sensor_part="Usage [kW]", last_updated_datetime=timestamps[0].subtract(seconds=60), is_active=True)
        conn.add(sensor_row)
        conn.commit()
        # get_data_from_api() adds 60 seconds to api_start_timestamp arg when making egauge api call
        frozen_time1 = timestamps[1]
        with freeze_time(time_to_freeze=frozen_time1):
            reading_dataframe1, purpose_sensors = api_egauge.get_data_from_api(conn, self.sensor_id)
        index1 = pandas.Index(reading_dataframe1['Date & Time'])
        #print contents of Date & Time column for visual verification if test fails
        print(index1)
        # reading_dataframe1.to_csv(path_or_buf='test_output.log', mode='a+')

        conn.query(orm_egauge.SensorInfo.purpose_id).filter(orm_egauge.SensorInfo.sensor_id == self.sensor_id).update({"last_updated_datetime": timestamps[1].subtract(seconds=60)})
        conn.commit()
        frozen_time2 = timestamps[2]
        with freeze_time(time_to_freeze=frozen_time2):
            reading_dataframe2, purpose_sensors = api_egauge.get_data_from_api(conn, self.sensor_id)
        index2 = pandas.Index(reading_dataframe2['Date & Time'])
        print(index2)
        # reading_dataframe2.to_csv(path_or_buf='test_output.log', mode='a+')

        frames = [reading_dataframe1, reading_dataframe2]
        concatenated_frame = pandas.concat(frames)
        conn.close()
        self.assertTrue(not any(concatenated_frame['Date & Time'].duplicated()))


    # test get_data_from_api() for missing rows by confirming
    # if the correct number of values are returned from an api request
    def test_api_requested_data_for_missing_rows(self):
        db = api_egauge.create_engine(self.db_url)
        Session = api_egauge.sessionmaker(db)
        conn = Session()
        start_timestamp = pendulum.parse('2019-02-01T00:00:00.000-10:00')
        end_timestamp = pendulum.parse('2019-02-01T00:15:44.100-10:00')
        #insert start_timestamp into database_insertion_timestamp
        sensor_row = orm_egauge.SensorInfo(sensor_id=self.sensor_id, sensor_type="egauge", purpose_id=1, sensor_part="Usage [kW]", last_updated_datetime=start_timestamp.subtract(seconds=60), is_active=True)
        conn.add(sensor_row)
        conn.commit()
        frozen_time = end_timestamp
        with freeze_time(time_to_freeze=frozen_time):
            reading_dataframe, purpose_sensors = api_egauge.get_data_from_api(conn, self.sensor_id)
        index = pandas.Index(reading_dataframe['Date & Time'])
        print(index)
        # get the difference in minutes between the start and end time
        diff = end_timestamp - start_timestamp
        minutes, remainder = divmod(diff.seconds, 60)
        conn.close()
        # Check if difference in minutes between the start and end
        # matches the number of rows in the reading_dataframe
        self.assertTrue(minutes == reading_dataframe.shape[0])


    """
    unit test example template

    def test_something(self): #name must begin with 'test_' if you want unittest.main() to automatically run it
        # write test code that runs your desired function in a certain way that creates a certain result
        # call an assert function that will return a boolean based on the result of your test code
        self.assertTrue(True)

    """


if __name__ == '__main__':
    unittest.main()
