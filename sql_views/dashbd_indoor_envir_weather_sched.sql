-- join readings in dashbd_indoorenv_weather_no_sched 
-- with class schedule in schedule_min
-- [used by NA] 
CREATE VIEW dashbd_indoor_envir_weather_sched AS 

 SELECT dashbd_indoorenv_weather_no_sched.datetime AS "Datetime",
    dashbd_indoorenv_weather_no_sched.building AS "Building",
    dashbd_indoorenv_weather_no_sched.type AS "Type",
    dashbd_indoorenv_weather_no_sched.appliance AS "Appliance",
    dashbd_indoorenv_weather_no_sched.room AS "Room",
    dashbd_indoorenv_weather_no_sched.surface AS "Surface",
    dashbd_indoorenv_weather_no_sched."Humidity (%)",
    dashbd_indoorenv_weather_no_sched."Temperature (F)",
    dashbd_indoorenv_weather_no_sched."Temperature (C)",
    dashbd_indoorenv_weather_no_sched."Light (lux)",
    dashbd_indoorenv_weather_no_sched."CO2 (ppm)",
    dashbd_indoorenv_weather_no_sched."Window",
    dashbd_indoorenv_weather_no_sched."Power Avg (kW)",
    dashbd_indoorenv_weather_no_sched."Solar radiation (w/m2)",
    dashbd_indoorenv_weather_no_sched."Wind speed (m/s)",
    dashbd_indoorenv_weather_no_sched."Wind direction (deg)",
    dashbd_indoorenv_weather_no_sched."Barometric pressure (hPa)",
    dashbd_indoorenv_weather_no_sched."Dewpoint (C)",
    dashbd_indoorenv_weather_no_sched."Dewpoint (F)",
    schedule_min.date AS "Date",
    schedule_min."time" AS "Time",
    schedule_min.schoolday AS "Schoolday"
   FROM dashbd_indoorenv_weather_no_sched
     FULL JOIN schedule_min ON dashbd_indoorenv_weather_no_sched.datetime = schedule_min.datetime AND dashbd_indoorenv_weather_no_sched.building::text = schedule_min.building::text;
