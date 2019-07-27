-- Grabs the "PV" appliance for all houses 
-- (sums all the data points for the same timestamp so that 
-- we get one data point per timestamp per building) 
-- [used by dashboard-union_of_views]
CREATE VIEW kat."dashboard-pv" AS 

 SELECT sensor_info.building,
    'PV'::character varying AS appliance,
    reading.datetime,
    reading.reading AS "Power Avg (kW)"
   FROM sensor_info
     JOIN reading ON reading.purpose_id = sensor_info.purpose_id
  WHERE sensor_info.purpose_id = ANY (ARRAY[94, 107]);
