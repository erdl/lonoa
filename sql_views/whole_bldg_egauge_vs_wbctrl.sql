-- compare whole building energy usage measured by egauge and webctrl
-- [used by NA]
CREATE VIEW whole_bldg_egauge_vs_wbctrl AS 

 SELECT reading.datetime,
    reading.purpose_id,
    reading.units,
    reading.reading AS "Power (kW)",
    sensor_info.building,
    sensor_info.variable_name
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE reading.purpose_id = ANY (ARRAY[96::bigint, 109::bigint, 84::bigint, 85::bigint]);
