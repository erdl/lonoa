-- calculate sum of instantaneous power for each building 
-- [used by power-readings-all]
CREATE VIEW "calc-other-inst-power" AS 

 SELECT calc.datetime,
    'kW'::character varying AS units,
    calc.building,
    'other-inst-calc'::character varying AS variable_name,
    'Power-instantaneous (kW)'::character varying AS type,
    'Other-calculated'::character varying AS appliance,
    NULL::double precision AS "Power avg (kW)",
    sum(calc.reading) AS "Power instantaneous (kW)"
   FROM ( SELECT reading.datetime,
            sensor_info.building,
            reading.reading
           FROM reading
             JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-inst%'::text AND sensor_info.appliance::text ~~ 'Whole building'::text
        UNION ALL
         SELECT reading.datetime,
            sensor_info.building,
            (- 1::double precision) * reading.reading AS reading
           FROM reading
             JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
          WHERE sensor_info.type::text ~~ 'Power-inst%'::text AND sensor_info.appliance::text !~~ 'Whole building'::text) calc
  GROUP BY calc.datetime, calc.building;
