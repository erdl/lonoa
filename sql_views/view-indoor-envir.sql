-- Grab conditions of indoor environment (like humidity, temp, light, co2, if windows are open) 
-- [used by dashboard-with-indoor-envir]
CREATE VIEW "view-indoor-envir" AS 

 SELECT reading.datetime,
    sensor_info.building,
    sensor_info.type,
    sensor_info.room,
    sensor_info.surface,
    max(
        CASE
            WHEN sensor_info.type::text = 'Humidity'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Humidity (%)",
    max(
        CASE
            WHEN sensor_info.type::text ~~ 'Temperature%%'::text AND reading.units::text = 'F'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Temperature (F)",
    max(
        CASE
            WHEN sensor_info.type::text = 'Light-lux'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Light (lux)",
    max(
        CASE
            WHEN sensor_info.type::text = 'CO2'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "CO2 (ppm)",
    max(
        CASE
            WHEN sensor_info.type::text = 'Window'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Window"
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone AND sensor_info.building::text !~~ 'weather%'::text AND (sensor_info.type::text = 'CO2'::text OR sensor_info.type::text = 'Light-lux'::text OR sensor_info.type::text ~~ 'Temperature%%'::text OR sensor_info.type::text ~~ 'Window'::text OR sensor_info.type::text = 'Humidity'::text)
  GROUP BY reading.datetime, reading.purpose_id, reading.units, sensor_info.building, sensor_info.variable_name, sensor_info.type, sensor_info.appliance, sensor_info.room, sensor_info.surface;
