-- grab frog-1 egauge readings from 2017-12-06 16:39:00 to 2017-12-07 16:38:00
-- [used by meter-comparison-1minute]
CREATE VIEW "meter-egauge-minute" AS 

 SELECT 'egauge' AS meter,
    reading.datetime AS "Datetime",
    reading.reading AS "Power (kW)"
   FROM reading
  WHERE reading.purpose_id = 84 AND reading.datetime >= '2017-12-06 16:39:00'::timestamp without time zone AND reading.datetime <= '2017-12-07 16:38:00'::timestamp without time zone;
