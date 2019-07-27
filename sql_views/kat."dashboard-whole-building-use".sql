-- Grabs the "Whole building use" appliance data from 
-- "dashboard-pv-pos-whole-building-net " (sums all the data points 
-- for the same timestamp so that we get one data point per timestamp per building) 
-- [used by dashboard-union_of_views]
CREATE VIEW kat."dashboard-whole-building-use" AS 

 SELECT "dashboard-pv-pos-whole-building-net".building,
    'Whole building use' AS appliance,
    "dashboard-pv-pos-whole-building-net".datetime,
    sum("dashboard-pv-pos-whole-building-net"."Power Avg (kW)") AS "Power Avg (kW)"
   FROM kat."dashboard-pv-pos-whole-building-net"
  GROUP BY "dashboard-pv-pos-whole-building-net".building, "dashboard-pv-pos-whole-building-net".datetime
  ORDER BY "dashboard-pv-pos-whole-building-net".building, "dashboard-pv-pos-whole-building-net".datetime;
