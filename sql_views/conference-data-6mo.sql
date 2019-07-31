-- grab non-egauge "Power-avg%" type readings from 2017-03-22 to 
-- 2017-09-21 
-- [used by NA]
CREATE VIEW "conference-data-6mo" AS 

 SELECT reading.datetime,
    reading.purpose_id,
    reading.units,
    reading.reading,
    reading.upload_timestamp,
    sensor_info.building,
    sensor_info.variable_name,
    sensor_info.appliance
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.type::text ~~ 'Power-avg%'::text AND sensor_info.variable_name::text !~~ 'egauge%'::text AND reading.datetime >= '2017-03-22 00:00:00'::timestamp without time zone AND reading.datetime < '2017-09-22 00:00:00'::timestamp without time zone;
