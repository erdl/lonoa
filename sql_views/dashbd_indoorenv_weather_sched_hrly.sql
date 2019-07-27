-- aggregate different readings by hourly average
-- [used by NA]
CREATE VIEW dashbd_indoorenv_weather_sched_hrly AS 

 SELECT dashbd_indoorenv_weatherstation_hrly."Datetime_hr",
    dashbd_indoorenv_weatherstation_hrly."Building",
    dashbd_indoorenv_weatherstation_hrly.aggregation,
    dashbd_indoorenv_weatherstation_hrly."Temperature_F",
    dashbd_indoorenv_weatherstation_hrly."Temperature_C",
    dashbd_indoorenv_weatherstation_hrly."Humidity_%",
    dashbd_indoorenv_weatherstation_hrly."Light (lux)",
    dashbd_indoorenv_weatherstation_hrly."CO2 (ppm)",
    dashbd_indoorenv_weatherstation_hrly."Power Avg (kW)",
    dashbd_indoorenv_weatherstation_hrly."Window",
    dashbd_indoorenv_weatherstation_hrly."Solar_radiation_w/m2",
    dashbd_indoorenv_weatherstation_hrly."Wind_speed_m/s",
    dashbd_indoorenv_weatherstation_hrly."Wind_direction_deg",
    dashbd_indoorenv_weatherstation_hrly."Barometric_pressure_hPa",
    dashbd_indoorenv_weatherstation_hrly."Dewpoint_C",
    dashbd_indoorenv_weatherstation_hrly."Dewpoint_F",
    dashbd_indoorenv_weatherstation_hrly.appliance,
    schedule_hr."Date",
    schedule_hr."Time",
    schedule_hr."Schoolday"
   FROM dashbd_indoorenv_weatherstation_hrly
     JOIN schedule_hr ON dashbd_indoorenv_weatherstation_hrly."Datetime_hr" = schedule_hr.datetime_hr AND dashbd_indoorenv_weatherstation_hrly."Building"::text = schedule_hr."Building"::text;
