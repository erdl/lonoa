-- get the positive or negative delta of co2 levels in frog-1 and frog-2
-- [used by dashbd_indoorenv_weatherstation_hrly] 
CREATE VIEW co2_difference_hrly AS 

 SELECT c.date_trunc,
    c.building,
        CASE
            WHEN c.time_max > c.time_min THEN c.reading_max - c.reading_min
            ELSE c.reading_min - c.reading_max
        END AS difference
   FROM ( SELECT a2.date_trunc,
            a2.building,
            a2.time_max,
            a2.reading_max,
            b2.time_min,
            b2.reading_min
           FROM ( SELECT a.reading AS reading_max,
                    a.building,
                    a.date_trunc,
                    max(a.datetime) AS time_max,
                    a.rank
                   FROM ( SELECT date_trunc('hour'::text, reading.datetime) AS date_trunc,
                            sensor_info.building,
                            reading.datetime,
                            reading.reading,
                            rank() OVER (PARTITION BY sensor_info.building, (date_trunc('hour'::text, reading.datetime)) ORDER BY reading.reading DESC) AS rank
                           FROM reading
                             JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
                          WHERE reading.purpose_id = ANY (ARRAY[81::bigint, 82::bigint])
                          ORDER BY (date_trunc('hour'::text, reading.datetime)), sensor_info.building, (rank() OVER (PARTITION BY sensor_info.building, (date_trunc('hour'::text, reading.datetime)) ORDER BY reading.reading DESC))) a
                  WHERE a.rank = 1
                  GROUP BY a.date_trunc, a.reading, a.building, a.rank
                  ORDER BY a.date_trunc, a.building) a2
             JOIN ( SELECT b.building,
                    b.date_trunc,
                    min(b.datetime) AS time_min,
                    b.reading AS reading_min
                   FROM ( SELECT date_trunc('hour'::text, reading.datetime) AS date_trunc,
                            sensor_info.building,
                            reading.datetime,
                            reading.reading,
                            rank() OVER (PARTITION BY sensor_info.building, (date_trunc('hour'::text, reading.datetime)) ORDER BY reading.reading) AS rank
                           FROM reading
                             JOIN sensor_info ON reading.purpose_id = sensor_info.purpose_id
                          WHERE reading.purpose_id = ANY (ARRAY[81::bigint, 82::bigint])
                          ORDER BY (date_trunc('hour'::text, reading.datetime)), sensor_info.building, (rank() OVER (PARTITION BY sensor_info.building, (date_trunc('hour'::text, reading.datetime)) ORDER BY reading.reading))) b
                  WHERE b.rank = 1
                  GROUP BY b.date_trunc, b.reading, b.building, b.rank
                  ORDER BY b.date_trunc, b.building) b2 ON a2.building::text = b2.building::text AND a2.date_trunc = b2.date_trunc) c;
