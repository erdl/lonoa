-- grabs dashbd-indoorenv-sched and displays alongside 
-- weather measurements set to null.
-- [used by dashbd_indoorenv_weatherstation]
CREATE VIEW "dashbd-indoorenv-sched-testweathercombine" AS 

 SELECT dashbd_indoorenv_sched.datetime,
    dashbd_indoorenv_sched.building,
    dashbd_indoorenv_sched."Temperature (F)" AS "Temperature_F",
    max(
        CASE
            WHEN dashbd_indoorenv_sched."Temperature (F)" IS NOT NULL THEN (dashbd_indoorenv_sched."Temperature (F)" - 32::double precision) * 5::double precision / 9::double precision
            ELSE NULL::double precision
        END) AS "Temperature_C",
    dashbd_indoorenv_sched."Humidity (%)" AS "Humidity_%",
    dashbd_indoorenv_sched."Light (lux)",
    dashbd_indoorenv_sched."CO2 (ppm)",
    dashbd_indoorenv_sched."Power Avg (kW)",
    dashbd_indoorenv_sched."Window",
    NULL::double precision AS "Solar_radiation_w/m2",
    NULL::double precision AS "Wind_speed_m/s",
    NULL::double precision AS "Wind_direction_deg",
    NULL::double precision AS "Barometric_pressure_hPa",
    NULL::double precision AS "Dewpoint_C",
    NULL::double precision AS "Dewpoint_F",
    dashbd_indoorenv_sched.instructor,
    dashbd_indoorenv_sched.teacher,
    dashbd_indoorenv_sched.class,
    dashbd_indoorenv_sched.dow,
    dashbd_indoorenv_sched.schoolday,
    dashbd_indoorenv_sched.session,
    dashbd_indoorenv_sched.type,
    dashbd_indoorenv_sched.appliance,
    dashbd_indoorenv_sched.room,
    dashbd_indoorenv_sched.surface,
    dashbd_indoorenv_sched.occ_sample,
    dashbd_indoorenv_sched.effective_occupancy,
    dashbd_indoorenv_sched."time",
    dashbd_indoorenv_sched.date
   FROM dashbd_indoorenv_sched
  GROUP BY dashbd_indoorenv_sched.datetime, dashbd_indoorenv_sched.building, dashbd_indoorenv_sched.instructor, dashbd_indoorenv_sched.class, dashbd_indoorenv_sched.dow, dashbd_indoorenv_sched.schoolday, dashbd_indoorenv_sched.session, dashbd_indoorenv_sched.type, dashbd_indoorenv_sched.appliance, dashbd_indoorenv_sched.room, dashbd_indoorenv_sched.surface, dashbd_indoorenv_sched."Humidity (%)", dashbd_indoorenv_sched."Temperature (F)", dashbd_indoorenv_sched."Light (lux)", dashbd_indoorenv_sched."CO2 (ppm)", dashbd_indoorenv_sched."Power Avg (kW)", dashbd_indoorenv_sched."Window", dashbd_indoorenv_sched.teacher, dashbd_indoorenv_sched.occ_sample, dashbd_indoorenv_sched.effective_occupancy, dashbd_indoorenv_sched."time", dashbd_indoorenv_sched.date
  ORDER BY dashbd_indoorenv_sched.datetime;
