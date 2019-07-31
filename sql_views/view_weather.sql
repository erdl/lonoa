-- grab readings where building='weather-station'
-- Eileen: used in another view;
-- to be dissolved into view_weather_only to simplify
-- [used by dashbd_indoorenv_weatherstation]
CREATE VIEW view_weather AS 

 SELECT reading.datetime,
    sensor_info.building,
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dry-bulb-temp'::text THEN 9::double precision * reading.reading / 5::double precision + 32::double precision
            ELSE NULL::double precision
        END) AS "Temperature_F",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dry-bulb-temp'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Temperature_C",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'humidity'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Humidity_%",
    NULL::double precision AS "Light (lux)",
    NULL::double precision AS "CO2 (ppm)",
    NULL::double precision AS "Power Avg (kW)",
    NULL::double precision AS "Window",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'solar-radiation'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Solar_radiation_w/m2",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'wind-speed'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Wind_speed_m/s",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'wind-direction'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Wind_direction_deg",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'barometric-pressure'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Barometric_pressure_hPa",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dewpoint'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Dewpoint_C",
    max(
        CASE
            WHEN sensor_info.variable_name::text ~~ 'dewpoint'::text THEN 9::double precision * reading.reading / 5::double precision + 32::double precision
            ELSE NULL::double precision
        END) AS "Dewpoint_F",
    NULL::character varying AS instructor,
    NULL::character varying AS teacher,
    NULL::character varying AS class,
    NULL::integer AS dow,
    NULL::integer AS schoolday,
    NULL::character varying AS session,
    NULL::character varying AS type,
    NULL::character varying AS appliance,
    NULL::character varying AS room,
    NULL::character varying AS surface,
    NULL::smallint AS occ_sample,
    NULL::integer AS effective_occupancy,
    NULL::time without time zone AS "time",
    NULL::date AS date
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.building::text ~~ 'weather-station'::text
  GROUP BY reading.datetime, sensor_info.building
  ORDER BY reading.datetime;
