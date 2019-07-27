-- Grabs the power readings for appliances: outdoor lights, ceiling fans, whole building net and whole
-- building net egauge (for both buildings) 
-- [used by dashboard-union_of views]

CREATE VIEW kat."dashboard-fans_and_outdoor_lights" AS 

( SELECT sensor_info.building,
    sensor_info.appliance,
    reading.datetime,
    reading.reading AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE (sensor_info.appliance::text ~ similar_escape('Outdoor lights controller|Ceiling fans|Whole building net%'::text, NULL::text) OR sensor_info.appliance::text = 'Whole building net egauge'::text) AND reading.datetime >= '2017-03-24 00:00:00'::timestamp without time zone AND sensor_info.type::text ~~ 'Power-avg%%'::text
  ORDER BY reading.datetime, sensor_info.building)
UNION
( SELECT sensor_info.building,
    sensor_info.appliance,
    reading.datetime,
    reading.reading AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.appliance::text ~ similar_escape('Outdoor lights controller|Ceiling fans|Whole building net%'::text, NULL::text) AND reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone AND reading.datetime <= '2017-03-24 00:00:00'::timestamp without time zone AND sensor_info.type::text ~~ 'Power-instantaneous%%'::text
  ORDER BY reading.datetime, sensor_info.building)
UNION
( SELECT sensor_info.building,
    sensor_info.appliance,
    reading.datetime,
    reading.reading AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.appliance::text = 'Whole building net egauge'::text AND reading.datetime <= '2017-03-24 00:00:00'::timestamp without time zone AND reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone AND sensor_info.type::text ~~ 'Power-avg%%'::text
  ORDER BY reading.datetime, sensor_info.building)
  ORDER BY 3, 1;
