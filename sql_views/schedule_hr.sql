-- view with datetime_hr column added to schedule_min table
-- [used by dashbd_indoorenv_weather_sched_hrly]

CREATE VIEW schedule_hr AS 

 SELECT date_trunc('hour'::text, schedule_min.datetime) AS datetime_hr,
    schedule_min.building AS "Building",
    date_trunc('day'::text, schedule_min.datetime) AS "Date",
    schedule_min.datetime::time without time zone AS "Time",
    max(schedule_min.schoolday) AS "Schoolday"
   FROM schedule_min
  GROUP BY (date_trunc('hour'::text, schedule_min.datetime)), schedule_min.building, (date_trunc('day'::text, schedule_min.datetime)), (schedule_min.datetime::time without time zone);
