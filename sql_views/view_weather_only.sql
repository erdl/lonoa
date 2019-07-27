-- grab weather related webctrl sensors readings only
-- [used by dashbd_indoorenv_weather_no_sched]
CREATE VIEW view_weather_only AS 

 SELECT reading.datetime,
    sensor_info.building,
    sensor_info.type,
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dry-bulb-temp'::text THEN 9::double precision * reading.reading / 5::double precision + 32::double precision
            ELSE NULL::double precision
        END) AS "Temperature (F)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dry-bulb-temp'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Temperature (C)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'humidity'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Humidity (%)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'solar-radiation'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Solar radiation (w/m2)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'wind-speed'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Wind speed (m/s)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'wind-direction'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Wind direction (deg)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'barometric-pressure'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Barometric pressure (hPa)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dewpoint'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Dewpoint (C)",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dewpoint'::text THEN 9::double precision * reading.reading / 5::double precision + 32::double precision
            ELSE NULL::double precision
        END) AS "Dewpoint (F)"
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.building::text ~~ 'weather-station'::text
  GROUP BY reading.datetime, sensor_info.building, sensor_info.type
  ORDER BY reading.datetime;
