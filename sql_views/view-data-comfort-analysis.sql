-- get classroom conditions (like temp, humidity) 
-- along with HVAC and fan power usage
-- [used by NA]
CREATE VIEW "view-data-comfort-analysis" AS 

 SELECT sensor_info.building,
    reading.datetime,
    max(
        CASE
            WHEN sensor_info.type::text = 'Temperature-air'::text AND sensor_info.room::text = 'Classroom'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Temperature-Air",
    max(
        CASE
            WHEN sensor_info.type::text = 'Temperature-mrt'::text AND sensor_info.room::text = 'Classroom'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Temperature-mrt",
    max(
        CASE
            WHEN sensor_info.type::text = 'Humidity'::text AND sensor_info.room::text = 'Classroom'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Humidity",
    max(
        CASE
            WHEN sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.variable_name::text = 'air-handler-avg'::text THEN reading.reading
            ELSE NULL::double precision
        END) + max(
        CASE
            WHEN sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.variable_name::text = 'chiller-avg'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "HVAC",
    max(
        CASE
            WHEN sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.variable_name::text = 'ceiling-fans-avg'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Ceiling fans"
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.building::text !~~ 'weather%'::text AND (sensor_info.purpose_id <> ALL (ARRAY[84, 85])) AND reading.datetime >= '2017-08-20 00:00:00'::timestamp without time zone AND reading.datetime < '2017-12-17 00:00:00'::timestamp without time zone
  GROUP BY sensor_info.building, reading.datetime;
