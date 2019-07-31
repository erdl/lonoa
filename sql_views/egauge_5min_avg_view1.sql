-- used to get egauge readings
-- assign a five minute incremented datetime to each egauge reading 
-- (:00, :05, :10, etc)
-- [used by eguage_5min_avg_view2]
CREATE VIEW egauge_5min_avg_view1 AS 

 SELECT reading.datetime,
        CASE
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[0, 1, 2, 3, 4]) THEN date_trunc('hour'::text, reading.datetime) + '00:05:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[5, 6, 7, 8, 9]) THEN date_trunc('hour'::text, reading.datetime) + '00:10:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[10, 11, 12, 13, 14]) THEN date_trunc('hour'::text, reading.datetime) + '00:15:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[15, 16, 17, 18, 19]) THEN date_trunc('hour'::text, reading.datetime) + '00:20:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[20, 21, 22, 23, 24]) THEN date_trunc('hour'::text, reading.datetime) + '00:25:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[25, 26, 27, 28, 29]) THEN date_trunc('hour'::text, reading.datetime) + '00:30:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[30, 31, 32, 33, 34]) THEN date_trunc('hour'::text, reading.datetime) + '00:35:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[35, 36, 37, 38, 39]) THEN date_trunc('hour'::text, reading.datetime) + '00:40:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[40, 41, 42, 43, 44]) THEN date_trunc('hour'::text, reading.datetime) + '00:45:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[45, 46, 47, 48, 49]) THEN date_trunc('hour'::text, reading.datetime) + '00:50:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[50, 51, 52, 53, 54]) THEN date_trunc('hour'::text, reading.datetime) + '00:55:00'::time without time zone::interval
            WHEN date_part('minute'::text, reading.datetime)::integer = ANY (ARRAY[55, 56, 57, 58, 59]) THEN date_trunc('hour'::text, reading.datetime) + '01:00:00'::time without time zone::interval
            ELSE NULL::timestamp without time zone
        END AS datetime_5min,
    reading.purpose_id,
    'kW'::character varying(255) AS units,
    reading.reading
   FROM reading
  WHERE reading.purpose_id = ANY (ARRAY[84, 85])
  ORDER BY reading.datetime, reading.purpose_id;
