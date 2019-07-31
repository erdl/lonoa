-- Grabs the "Plugloads" appliance for all houses 
-- (sums all the data points for the same timestamp so that we 
-- get one data point per timestamp per building) 
-- [used by dashboard-union_of_views]
CREATE VIEW kat."dashboard-plugloads" AS 

 SELECT "dashboard-readings-neg".building,
    'Plugloads'::character varying AS appliance,
    "dashboard-readings-neg".datetime,
    sum("dashboard-readings-neg".reading_negs) AS "Power Avg (kW)"
   FROM kat."dashboard-readings-neg"
  GROUP BY "dashboard-readings-neg".building, "dashboard-readings-neg".datetime
  ORDER BY "dashboard-readings-neg".building, "dashboard-readings-neg".datetime;
