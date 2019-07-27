-- Displays earliest and latest reading datetimes 
-- along with the last upload datetime for each sensor.
-- Useful for figuring out if readings are not being obtained from a sensor
-- [used by NA]
CREATE VIEW dates_reading AS 

 SELECT reading.purpose_id,
    min(reading.datetime) AS min,
    max(reading.datetime) AS max,
    max(reading.upload_timestamp) AS "Last upload",
    sensor_info.building,
    sensor_info.variable_name
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  GROUP BY reading.purpose_id, sensor_info.building, sensor_info.variable_name
  ORDER BY reading.purpose_id;
