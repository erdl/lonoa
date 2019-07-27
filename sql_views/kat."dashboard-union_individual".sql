-- Description: Combines dashboard-readings-neg and dashboard-pv-pos-whole-building-net 
-- [used by dashboard-with-indoor-env, dashbd_indoorenv_weather_no_sched] 
CREATE VIEW kat."dashboard-union_individual" AS 

( SELECT "dashboard-readings-neg".building,
    'Plugloads'::character varying AS appliance,
    "dashboard-readings-neg".datetime,
    sum("dashboard-readings-neg".reading_negs) AS "Power Avg (kW)"
   FROM kat."dashboard-readings-neg"
  GROUP BY "dashboard-readings-neg".building, "dashboard-readings-neg".datetime
  ORDER BY "dashboard-readings-neg".building, "dashboard-readings-neg".datetime)
UNION
( SELECT sensor_info.building,
    'Ceiling fans 1 north'::character varying AS appliance,
    reading.datetime,
    sum(reading.reading) AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.type::text ~~ 'Power-avg%%'::text AND sensor_info.appliance::text ~~ 'Ceiling fans 1 north'::text
  GROUP BY sensor_info.building, reading.datetime
  ORDER BY reading.datetime, sensor_info.building)
UNION
( SELECT sensor_info.building,
    'Ceiling fans 2 south'::character varying AS appliance,
    reading.datetime,
    sum(reading.reading) AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.type::text ~~ 'Power-avg%%'::text AND sensor_info.appliance::text ~~ 'Ceiling fans 2 south'::text
  GROUP BY sensor_info.building, reading.datetime
  ORDER BY reading.datetime, sensor_info.building)
UNION
( SELECT sensor_info.building,
    'Ceiling fans 3 middle'::character varying AS appliance,
    reading.datetime,
    sum(reading.reading) AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.type::text ~~ 'Power-avg%%'::text AND sensor_info.appliance::text ~~ 'Ceiling fans 3 middle'::text
  GROUP BY sensor_info.building, reading.datetime
  ORDER BY reading.datetime, sensor_info.building)
UNION (
        ( SELECT sensor_info.building,
            'Indoor Lights'::character varying AS appliance,
            reading.datetime,
            sum(reading.reading) AS "Power Avg (kW)"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-avg%%'::text AND sensor_info.appliance::text ~~ 'Indoor lights%%'::text AND reading.datetime >= '2017-03-24 00:00:00'::timestamp without time zone
          GROUP BY sensor_info.building, reading.datetime
          ORDER BY reading.datetime, sensor_info.building)
        UNION
        ( SELECT sensor_info.building,
            'Indoor Lights'::character varying AS appliance,
            reading.datetime,
            sum(reading.reading) AS "Power Avg (kW)"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-instantaneous%%'::text AND sensor_info.appliance::text ~~ 'Indoor lights%%'::text AND reading.datetime <= '2017-03-24 00:00:00'::timestamp without time zone AND reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone
          GROUP BY sensor_info.building, reading.datetime
          ORDER BY reading.datetime, sensor_info.building)
)
UNION (
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
)
UNION (
        ( SELECT sensor_info.building,
            'AHU'::character varying AS appliance,
            reading.datetime,
            sum(reading.reading) AS "Power Avg (kW)"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-avg%%'::text AND sensor_info.appliance::text ~~ 'AC air handling unit'::text AND reading.datetime >= '2017-03-24 00:00:00'::timestamp without time zone
          GROUP BY sensor_info.building, reading.datetime
          ORDER BY reading.datetime, sensor_info.building)
        UNION
        ( SELECT sensor_info.building,
            'AHU'::character varying AS appliance,
            reading.datetime,
            sum(reading.reading) AS "Power Avg (kW)"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-instantaneous%%'::text AND sensor_info.appliance::text ~~ 'AC air handling unit'::text AND reading.datetime <= '2017-03-24 00:00:00'::timestamp without time zone AND reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone
          GROUP BY sensor_info.building, reading.datetime
          ORDER BY reading.datetime, sensor_info.building)
)
UNION (
        ( SELECT sensor_info.building,
            'ACC'::character varying AS appliance,
            reading.datetime,
            sum(reading.reading) AS "Power Avg (kW)"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-avg%%'::text AND sensor_info.appliance::text ~~ 'AC chiller'::text AND reading.datetime >= '2017-03-24 00:00:00'::timestamp without time zone
          GROUP BY sensor_info.building, reading.datetime
          ORDER BY reading.datetime, sensor_info.building)
        UNION
        ( SELECT sensor_info.building,
            'ACC'::character varying AS appliance,
            reading.datetime,
            sum(reading.reading) AS "Power Avg (kW)"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-instantaneous%%'::text AND sensor_info.appliance::text ~~ 'AC chiller'::text AND reading.datetime <= '2017-03-24 00:00:00'::timestamp without time zone AND reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone
          GROUP BY sensor_info.building, reading.datetime
          ORDER BY reading.datetime, sensor_info.building)
)
UNION (
         SELECT sensor_info.building,
            sensor_info.appliance,
            reading.datetime,
            reading.reading AS "Power Avg (kW)"
           FROM reading
             JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
          WHERE reading.purpose_id = ANY (ARRAY[96::bigint, 109::bigint])
        UNION
         SELECT sensor_info.building,
            'Whole building net'::character varying(30) AS appliance,
            eguage_5min_avg_view2.datetime_5min::timestamp(6) without time zone AS datetime,
            eguage_5min_avg_view2.avg AS "Power Avg (kW)"
           FROM eguage_5min_avg_view2
             JOIN sensor_info ON sensor_info.purpose_id = eguage_5min_avg_view2.purpose_id
          WHERE eguage_5min_avg_view2.datetime_5min >= '2018-01-01 00:00:00'::timestamp without time zone AND eguage_5min_avg_view2.datetime_5min < '2018-01-31 00:00:00'::timestamp without time zone
)
UNION
 SELECT sensor_info.building,
    'PV'::character varying AS appliance,
    reading.datetime,
    reading.reading AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.purpose_id = ANY (ARRAY[94, 107])
UNION
( SELECT "dashboard-pv-pos-whole-building-net".building,
    'Whole building use'::character varying AS appliance,
    "dashboard-pv-pos-whole-building-net".datetime,
    sum("dashboard-pv-pos-whole-building-net"."Power Avg (kW)") AS "Power Avg (kW)"
   FROM kat."dashboard-pv-pos-whole-building-net"
  GROUP BY "dashboard-pv-pos-whole-building-net".building, "dashboard-pv-pos-whole-building-net".datetime
  ORDER BY "dashboard-pv-pos-whole-building-net".building, "dashboard-pv-pos-whole-building-net".datetime)
UNION (
        ( SELECT sensor_info.building,
            sensor_info.appliance,
            reading.datetime,
            reading.reading AS "Power Avg (kW)"
           FROM sensor_info
             JOIN reading ON reading.purpose_id = sensor_info.purpose_id
          WHERE (sensor_info.appliance::text ~ similar_escape('Outdoor lights controller|Ceiling fans|Whole building%'::text, NULL::text) OR sensor_info.appliance::text = 'Whole building net egauge'::text) AND reading.datetime >= '2017-03-24 00:00:00'::timestamp without time zone AND sensor_info.type::text ~~ 'Power-avg%%'::text
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
)
  ORDER BY 3, 1;
