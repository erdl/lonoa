-- grab power readings where type ~~ 'Power-avg%%' or 'Power-inst%%'
-- [used by NA]

CREATE VIEW "view-as-columns-all-power" AS 

 SELECT reading.datetime,
    reading.units,
    sensor_info.building,
    sensor_info.variable_name,
    sensor_info.type,
    sensor_info.appliance,
    max(
        CASE
            WHEN sensor_info.type::text ~~ 'Power-avg%%'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Power avg(kW)",
    max(
        CASE
            WHEN sensor_info.type::text ~~ 'Power-inst%%'::text THEN reading.reading
            ELSE NULL::double precision
        END) AS "Power instantaneous(kW)"
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone AND sensor_info.type::text ~~ 'Power%'::text
  GROUP BY reading.datetime, reading.purpose_id, reading.units, sensor_info.building, sensor_info.variable_name, sensor_info.type, sensor_info.appliance, sensor_info.room, sensor_info.surface;
