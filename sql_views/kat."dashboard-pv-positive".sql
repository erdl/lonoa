-- Description: Does the same thing as "dashboard-pv", but multiplies every data
-- point by "-1" to get positive values 
-- [used by NA]
CREATE VIEW kat."dashboard-pv-positive" AS 

 SELECT sensor_info.building,
    'PV'::character varying AS appliance,
    reading.datetime,
    '-1'::integer::double precision * reading.reading AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.purpose_id = ANY (ARRAY[94, 107]);
