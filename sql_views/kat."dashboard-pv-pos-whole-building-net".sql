-- Does the same thing as "dashboard-pv-positive", 
-- but adds the appliance "Whole building net" 
-- (there was no good data for "Whole building net" between 
-- 2018-01-01 and 2018-01-31, so the 5-min trailing avg of 
-- "Whole building net egauge" was used as "Whole building net" 
-- for that date range) 
-- [used by dashboard-union_individual and dashboard-whole-building-use] 
CREATE VIEW kat."dashboard-pv-pos-whole-building-net" AS 

 SELECT sensor_info.building,
    'PV'::character varying AS appliance,
    reading.datetime,
    '-1'::integer::double precision * reading.reading AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.purpose_id = ANY (ARRAY[94, 107])
UNION
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
  WHERE eguage_5min_avg_view2.datetime_5min >= '2018-01-01 00:00:00'::timestamp without time zone AND eguage_5min_avg_view2.datetime_5min < '2018-01-31 00:00:00'::timestamp without time zone;
