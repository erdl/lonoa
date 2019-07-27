-- display non-egauge reading.reading values in different columns based on their sensor_info.type
-- [used by NA]
CREATE VIEW "view-readings-as-columns" AS 

 SELECT reading.datetime,
    reading.purpose_id,
    reading.units,
    sensor_info.building,
    sensor_info.variable_name,
    sensor_info.type,
    sensor_info.appliance,
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
            WHEN sensor_info.type::text = 'Energy-cumulative'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Energy cumulative (kWh)",
    max(
        CASE
            WHEN sensor_info.type::text ~~ 'Power-avg%%'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Power avg(kW)",
    max(
        CASE
            WHEN sensor_info.type::text ~~ 'Power-inst%%'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Power instantaneous(kW)",
    max(
        CASE
            WHEN sensor_info.type::text = 'Light-lux'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Light (lux)",
    max(
        CASE
            WHEN sensor_info.type::text = 'CO2'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "CO2 (ppm)"
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone AND (reading.purpose_id <> ALL (ARRAY[84::bigint, 85::bigint]))
  GROUP BY reading.datetime, reading.purpose_id, reading.units, sensor_info.building, sensor_info.variable_name, sensor_info.type, sensor_info.appliance, sensor_info.room, sensor_info.surface;
