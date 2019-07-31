-- grab classroom usage and reading data by
-- joining schedule_min table with dashboard-with-indoor-envir
-- [used by dashbd-indoorenv-sched-testweathercombine]
CREATE VIEW dashbd_indoorenv_sched AS 

 SELECT schedule_min.instructor,
    schedule_min.class,
    schedule_min.dow,
    schedule_min.schoolday,
    "dashboard-with-indoor-envir".building,
    schedule_min.session,
    "dashboard-with-indoor-envir".datetime,
    "dashboard-with-indoor-envir".type,
    "dashboard-with-indoor-envir".appliance,
    "dashboard-with-indoor-envir".room,
    "dashboard-with-indoor-envir".surface,
    "dashboard-with-indoor-envir"."Humidity (%)",
    "dashboard-with-indoor-envir"."Temperature (F)",
    "dashboard-with-indoor-envir"."Light (lux)",
    "dashboard-with-indoor-envir"."CO2 (ppm)",
    "dashboard-with-indoor-envir"."Power Avg (kW)",
    "dashboard-with-indoor-envir"."Window",
    schedule_min.teacher,
    schedule_min.occ_sample,
    schedule_min.effective_occupancy,
    schedule_min."time",
    schedule_min.date
   FROM schedule_min
     FULL JOIN "dashboard-with-indoor-envir" ON "dashboard-with-indoor-envir".datetime = schedule_min.datetime AND "dashboard-with-indoor-envir".building::text = schedule_min.building::text;
