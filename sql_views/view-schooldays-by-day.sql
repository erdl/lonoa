-- grab each day and schoolday value from schedule min for frog-1
-- [used by NA]

CREATE VIEW "view-schooldays-by-day" AS 

 SELECT DISTINCT date_trunc('day'::text, schedule_min.datetime) AS date,
    schedule_min.schoolday
   FROM schedule_min
  WHERE schedule_min.building::text = 'frog-1'::text
  ORDER BY (date_trunc('day'::text, schedule_min.datetime));
