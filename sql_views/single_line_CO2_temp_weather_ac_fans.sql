-- grab indoor conditions along with fan and AC power usage,
-- displaying all units for the same time increment in one row
-- [used by NA]
CREATE VIEW single_line_CO2_temp_weather_ac_fans AS 

 SELECT 'frog-1'::text AS building,
    frog1.datetime,
    frog1."Indoor temperature C",
    frog1."Indoor relative humdity %",
    frog1."Indoor CO2 ppm",
    frog1."Outdoor temperature C",
    frog1."Outdoor relative humdity %",
    frog1."Wind direction, deg",
    frog1."Wind speed m/s",
    frog1."Solar irradiance W/m2",
    frog1."Outdoor Barometric pressure hPa",
    frog1."Outdoor dewpoint temperature C",
    frog1."AC air handling unit power kW",
    frog1."AC chiller power kW",
    frog1."Ceiling fans 1 north power kW",
    frog1."Ceiling fans 1 middle power kW",
    frog1."Ceiling fans 1 south power kW"
   FROM ( SELECT reading.datetime,
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.room::text = 'Classroom'::text AND sensor_info.type::text = 'Temperature-air'::text THEN round((reading.reading::numeric - 32::numeric) * 5::numeric / 9::numeric, 2)
                    ELSE NULL::numeric
                END) AS "Indoor temperature C",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.room::text = 'Classroom'::text AND sensor_info.type::text = 'Humidity'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Indoor relative humdity %",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.room::text = 'Classroom'::text AND sensor_info.type::text = 'CO2'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Indoor CO2 ppm",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Temperature-exterior air'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor temperature C",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Humidity-exterior'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor relative humdity %",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Wind direction'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Wind direction, deg",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Wind-speed'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Wind speed m/s",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Light-w/m2'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Solar irradiance W/m2",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Barometric-pressure'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor Barometric pressure hPa",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Temperature-exterior dewpoint'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor dewpoint temperature C",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC air handling unit'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "AC air handling unit power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "AC chiller power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Ceiling fans 1 north power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Ceiling fans 1 middle power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-1'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Ceiling fans 1 south power kW"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.building::text !~~ 'frog-2'::text AND (sensor_info.purpose_id <> ALL (ARRAY[84, 85]))
          GROUP BY reading.datetime
          ORDER BY reading.datetime) frog1
UNION
 SELECT 'frog-2'::text AS building,
    frog2.datetime,
    frog2."Indoor temperature C",
    frog2."Indoor relative humdity %",
    frog2."Indoor CO2 ppm",
    frog2."Outdoor temperature C",
    frog2."Outdoor relative humdity %",
    frog2."Wind direction, deg",
    frog2."Wind speed m/s",
    frog2."Solar irradiance W/m2",
    frog2."Outdoor Barometric pressure hPa",
    frog2."Outdoor dewpoint temperature C",
    frog2."AC air handling unit power kW",
    frog2."AC chiller power kW",
    frog2."Ceiling fans 1 north power kW",
    frog2."Ceiling fans 1 middle power kW",
    frog2."Ceiling fans 1 south power kW"
   FROM ( SELECT reading.datetime,
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.room::text = 'Classroom'::text AND sensor_info.type::text = 'Temperature-air'::text THEN round((reading.reading::numeric - 32::numeric) * 5::numeric / 9::numeric, 2)
                    ELSE NULL::numeric
                END) AS "Indoor temperature C",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.room::text = 'Classroom'::text AND sensor_info.type::text = 'Humidity'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Indoor relative humdity %",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.room::text = 'Classroom'::text AND sensor_info.type::text = 'CO2'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Indoor CO2 ppm",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Temperature-exterior air'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor temperature C",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Humidity-exterior'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor relative humdity %",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Wind direction'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Wind direction, deg",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Wind-speed'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Wind speed m/s",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Light-w/m2'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Solar irradiance W/m2",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Barometric-pressure'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor Barometric pressure hPa",
            max(
                CASE
                    WHEN sensor_info.building::text = 'weather-station'::text AND sensor_info.type::text = 'Temperature-exterior dewpoint'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Outdoor dewpoint temperature C",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC air handling unit'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "AC air handling unit power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "AC chiller power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Ceiling fans 1 north power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Ceiling fans 1 middle power kW",
            max(
                CASE
                    WHEN sensor_info.building::text = 'frog-2'::text AND sensor_info.type::text = 'Power-avg (kW)'::text AND sensor_info.appliance::text = 'AC chiller'::text THEN reading.reading
                    ELSE NULL::double precision
                END) AS "Ceiling fans 1 south power kW"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.building::text !~~ 'frog-1'::text AND (sensor_info.purpose_id <> ALL (ARRAY[84, 85]))
          GROUP BY reading.datetime
          ORDER BY reading.datetime) frog2
  ORDER BY 2, 1;
