-- Grabs the appliance "Whole building net". 
-- Grabs the negative value of the appliances: 
-- Solar%, Other%, Fire%, Telecom%, Window%, and PV. 
-- (there was no good data for "Whole building net" between 2018-01-01 
-- and 2018-01-31, so the 5-min trailing avg of "Whole building net egauge" 
-- was used as "Whole building net" for that date range) 
-- [used by dashboard-union-individual and dashboard-plugloads]
CREATE VIEW kat."dashboard-readings-neg" AS 

( SELECT sensor_info.building,
    sensor_info.appliance,
    reading.datetime,
    max(
        CASE
            WHEN sensor_info.appliance::text ~~ 'Whole building net'::text THEN reading.reading
            ELSE (- 1::double precision) * reading.reading
        END) AS reading_negs
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE reading.datetime >= '2017-03-24 00:00:00'::timestamp without time zone AND sensor_info.type::text ~~ 'Power-avg%'::text AND sensor_info.variable_name::text !~~ 'egauge%'::text AND sensor_info.appliance::text !~ similar_escape('Solar%|Other%|Fire%|Telecom%|Window%'::text, NULL::text)
  GROUP BY sensor_info.building, sensor_info.appliance, reading.datetime
  ORDER BY sensor_info.building, reading.datetime)
UNION
( SELECT sensor_info.building,
    sensor_info.appliance,
    reading.datetime,
    max(
        CASE
            WHEN sensor_info.appliance::text ~~ 'Whole building net'::text THEN reading.reading
            ELSE (- 1::double precision) * reading.reading
        END) AS reading_negs
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE reading.datetime <= '2017-03-24 00:00:00'::timestamp without time zone AND reading.datetime >= '2017-01-01 00:00:00'::timestamp without time zone AND sensor_info.type::text ~~ 'Power-instantaneous%'::text AND sensor_info.variable_name::text !~~ 'egauge%'::text AND sensor_info.appliance::text !~ similar_escape('Solar%|Other%|Fire%|Telecom%|Window%'::text, NULL::text)
  GROUP BY sensor_info.building, sensor_info.appliance, reading.datetime
  ORDER BY sensor_info.building, reading.datetime)
UNION
( SELECT sensor_info.building,
    'PV'::character varying(30) AS appliance,
    reading.datetime,
    '-1'::integer::double precision * reading.reading AS reading_negs
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.purpose_id = ANY (ARRAY[94, 107])
  ORDER BY reading.datetime, sensor_info.building)
UNION
 SELECT sensor_info.building,
    'Whole building net'::character varying(30) AS appliance,
    eguage_5min_avg_view2.datetime_5min::timestamp(6) without time zone AS datetime,
    eguage_5min_avg_view2.avg AS reading_negs
   FROM eguage_5min_avg_view2
     JOIN sensor_info ON sensor_info.purpose_id = eguage_5min_avg_view2.purpose_id
  WHERE eguage_5min_avg_view2.datetime_5min >= '2018-01-01 00:00:00'::timestamp without time zone AND eguage_5min_avg_view2.datetime_5min < '2018-01-31 00:00:00'::timestamp without time zone;
