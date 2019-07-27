-- Grabs the "HVAC" appliance for all houses 
-- (sums all the data points for the same timestamp so that 
-- we get one data point per timestamp per building) 
-- [used by dashboard-union_of_views] 
CREATE VIEW kat."dashboard-hvac" AS 

( SELECT sensor_info.building,
    'HVAC'::character varying AS appliance,
    reading.datetime,
    sum(reading.reading) AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.type::text ~~ 'Power-avg%%'::text AND sensor_info.appliance::text ~~ 'AC%%'::text AND reading.datetime >= '2017-03-24 00:00:00'::timestamp without time zone
  GROUP BY sensor_info.building, reading.datetime
  ORDER BY reading.datetime, sensor_info.building)
UNION
( SELECT sensor_info.building,
    'HVAC'::character varying AS appliance,
    reading.datetime,
    sum(reading.reading) AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.type::text ~~ 'Power-instantaneous%%'::text AND sensor_info.appliance::text ~~ 'AC%%'::text AND reading.datetime <= '2017-03-24 00:00:00'::timestamp without time zone AND reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone
  GROUP BY sensor_info.building, reading.datetime
  ORDER BY reading.datetime, sensor_info.building)
  ORDER BY 3, 1;
