-- Averages egauge readings in 5 minute increments 
-- [used by dashboard-pv-pos-whole-building-net, dashboard-readings-neg,
-- dashboard-whole-building-net]
CREATE VIEW eguage_5min_avg_view2 AS 

 SELECT egauge_5min_avg_view1.datetime_5min,
    egauge_5min_avg_view1.purpose_id,
    egauge_5min_avg_view1.units,
    avg(egauge_5min_avg_view1.reading) AS avg
   FROM egauge_5min_avg_view1
  GROUP BY egauge_5min_avg_view1.datetime_5min, egauge_5min_avg_view1.purpose_id, egauge_5min_avg_view1.units
  ORDER BY egauge_5min_avg_view1.datetime_5min, egauge_5min_avg_view1.purpose_id;
