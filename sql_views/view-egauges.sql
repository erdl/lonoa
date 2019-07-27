-- DESCRIPTION:
-- get frog building egauge readings for the month of december 2017
-- [used by NA]
CREATE VIEW "view-egauges" AS 

 SELECT sensor_info.building,
    reading.datetime,
    reading.reading
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.variable_name::text ~~ 'egauge%'::text AND reading.datetime >= '2017-12-01 00:00:00'::timestamp without time zone AND reading.datetime < '2018-01-01 00:00:00'::timestamp without time zone;
