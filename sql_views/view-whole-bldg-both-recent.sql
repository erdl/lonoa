-- grab readings on or after January 26, 2018
-- [used by NA]
CREATE VIEW "view-whole-bldg-both-recent" AS 

 SELECT sensor_info.building,
    sensor_info.appliance,
    reading.datetime,
    reading.reading
   FROM reading
     JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
  WHERE (reading.purpose_id = ANY (ARRAY[84::bigint, 85::bigint, 96::bigint, 109::bigint])) AND reading.datetime >= '2018-01-26 00:00:00'::timestamp without time zone;
