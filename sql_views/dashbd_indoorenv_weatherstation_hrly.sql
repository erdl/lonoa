-- Grab hourly aggregates (like average, min, max, delta, difference, etc.) of readings 
-- from dashbd_indoorenv_weatherstation and co2_difference_hrly
-- [used by dashbd_indoorenv_weather_sched_hrly]
CREATE VIEW dashbd_indoorenv_weatherstation_hrly AS 

 SELECT date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime) AS "Datetime_hr",
    dashbd_indoorenv_weatherstation.building AS "Building",
    'average'::text AS aggregation,
    avg(dashbd_indoorenv_weatherstation."Temperature_F") AS "Temperature_F",
    avg(dashbd_indoorenv_weatherstation."Temperature_C") AS "Temperature_C",
    avg(dashbd_indoorenv_weatherstation."Humidity_%") AS "Humidity_%",
    avg(dashbd_indoorenv_weatherstation."Light (lux)") AS "Light (lux)",
    avg(dashbd_indoorenv_weatherstation."CO2 (ppm)") AS "CO2 (ppm)",
    avg(dashbd_indoorenv_weatherstation."Power Avg (kW)") AS "Power Avg (kW)",
    avg(dashbd_indoorenv_weatherstation."Window") AS "Window",
    avg(dashbd_indoorenv_weatherstation."Solar_radiation_w/m2") AS "Solar_radiation_w/m2",
    avg(dashbd_indoorenv_weatherstation."Wind_speed_m/s") AS "Wind_speed_m/s",
    avg(dashbd_indoorenv_weatherstation."Wind_direction_deg") AS "Wind_direction_deg",
    avg(dashbd_indoorenv_weatherstation."Barometric_pressure_hPa") AS "Barometric_pressure_hPa",
    avg(dashbd_indoorenv_weatherstation."Dewpoint_C") AS "Dewpoint_C",
    avg(dashbd_indoorenv_weatherstation."Dewpoint_F") AS "Dewpoint_F",
    dashbd_indoorenv_weatherstation.appliance
   FROM dashbd_indoorenv_weatherstation
  GROUP BY (date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime)), dashbd_indoorenv_weatherstation.building, dashbd_indoorenv_weatherstation.appliance
UNION ALL
 SELECT date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime) AS "Datetime_hr",
    dashbd_indoorenv_weatherstation.building AS "Building",
    'max'::text AS aggregation,
    max(dashbd_indoorenv_weatherstation."Temperature_F") AS "Temperature_F",
    max(dashbd_indoorenv_weatherstation."Temperature_C") AS "Temperature_C",
    max(dashbd_indoorenv_weatherstation."Humidity_%") AS "Humidity_%",
    NULL::double precision AS "Light (lux)",
    max(dashbd_indoorenv_weatherstation."CO2 (ppm)") AS "CO2 (ppm)",
    NULL::double precision AS "Power Avg (kW)",
    NULL::double precision AS "Window",
    NULL::double precision AS "Solar_radiation_w/m2",
    NULL::double precision AS "Wind_speed_m/s",
    NULL::double precision AS "Wind_direction_deg",
    NULL::double precision AS "Barometric_pressure_hPa",
    NULL::double precision AS "Dewpoint_C",
    NULL::double precision AS "Dewpoint_F",
    dashbd_indoorenv_weatherstation.appliance
   FROM dashbd_indoorenv_weatherstation
  WHERE dashbd_indoorenv_weatherstation."CO2 (ppm)" IS NOT NULL OR dashbd_indoorenv_weatherstation."Temperature_F" IS NOT NULL OR dashbd_indoorenv_weatherstation."Temperature_C" IS NOT NULL OR dashbd_indoorenv_weatherstation."Humidity_%" IS NOT NULL
  GROUP BY (date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime)), dashbd_indoorenv_weatherstation.building, dashbd_indoorenv_weatherstation.appliance
UNION ALL
 SELECT date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime) AS "Datetime_hr",
    dashbd_indoorenv_weatherstation.building AS "Building",
    'min'::text AS aggregation,
    min(dashbd_indoorenv_weatherstation."Temperature_F") AS "Temperature_F",
    min(dashbd_indoorenv_weatherstation."Temperature_C") AS "Temperature_C",
    min(dashbd_indoorenv_weatherstation."Humidity_%") AS "Humidity_%",
    NULL::double precision AS "Light (lux)",
    min(dashbd_indoorenv_weatherstation."CO2 (ppm)") AS "CO2 (ppm)",
    NULL::double precision AS "Power Avg (kW)",
    NULL::double precision AS "Window",
    NULL::double precision AS "Solar_radiation_w/m2",
    NULL::double precision AS "Wind_speed_m/s",
    NULL::double precision AS "Wind_direction_deg",
    NULL::double precision AS "Barometric_pressure_hPa",
    NULL::double precision AS "Dewpoint_C",
    NULL::double precision AS "Dewpoint_F",
    dashbd_indoorenv_weatherstation.appliance
   FROM dashbd_indoorenv_weatherstation
  WHERE dashbd_indoorenv_weatherstation."CO2 (ppm)" IS NOT NULL OR dashbd_indoorenv_weatherstation."Temperature_F" IS NOT NULL OR dashbd_indoorenv_weatherstation."Temperature_C" IS NOT NULL OR dashbd_indoorenv_weatherstation."Humidity_%" IS NOT NULL
  GROUP BY (date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime)), dashbd_indoorenv_weatherstation.building, dashbd_indoorenv_weatherstation.appliance
UNION ALL
 SELECT date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime) AS "Datetime_hr",
    dashbd_indoorenv_weatherstation.building AS "Building",
    'delta (max-min)'::text AS aggregation,
    avg(dashbd_indoorenv_weatherstation."Temperature_F") AS "Temperature_F",
    avg(dashbd_indoorenv_weatherstation."Temperature_C") AS "Temperature_C",
    avg(dashbd_indoorenv_weatherstation."Humidity_%") AS "Humidity_%",
    avg(dashbd_indoorenv_weatherstation."Light (lux)") AS "Light (lux)",
    max(dashbd_indoorenv_weatherstation."CO2 (ppm)") - min(dashbd_indoorenv_weatherstation."CO2 (ppm)") AS "CO2 (ppm)",
    avg(dashbd_indoorenv_weatherstation."Power Avg (kW)") AS "Power Avg (kW)",
    avg(dashbd_indoorenv_weatherstation."Window") AS "Window",
    avg(dashbd_indoorenv_weatherstation."Solar_radiation_w/m2") AS "Solar_radiation_w/m2",
    avg(dashbd_indoorenv_weatherstation."Wind_speed_m/s") AS "Wind_speed_m/s",
    avg(dashbd_indoorenv_weatherstation."Wind_direction_deg") AS "Wind_direction_deg",
    avg(dashbd_indoorenv_weatherstation."Barometric_pressure_hPa") AS "Barometric_pressure_hPa",
    avg(dashbd_indoorenv_weatherstation."Dewpoint_C") AS "Dewpoint_C",
    avg(dashbd_indoorenv_weatherstation."Dewpoint_F") AS "Dewpoint_F",
    dashbd_indoorenv_weatherstation.appliance
   FROM dashbd_indoorenv_weatherstation
  WHERE dashbd_indoorenv_weatherstation."CO2 (ppm)" IS NOT NULL
  GROUP BY (date_trunc('hour'::text, dashbd_indoorenv_weatherstation.datetime)), dashbd_indoorenv_weatherstation.building, dashbd_indoorenv_weatherstation.appliance
UNION ALL
 SELECT co2_difference_hrly.date_trunc AS "Datetime_hr",
    co2_difference_hrly.building AS "Building",
    'difference (max-min)'::text AS aggregation,
    NULL::double precision AS "Temperature_F",
    NULL::double precision AS "Temperature_C",
    NULL::double precision AS "Humidity_%",
    NULL::double precision AS "Light (lux)",
    co2_difference_hrly.difference AS "CO2 (ppm)",
    NULL::double precision AS "Power Avg (kW)",
    NULL::double precision AS "Window",
    NULL::double precision AS "Solar_radiation_w/m2",
    NULL::double precision AS "Wind_speed_m/s",
    NULL::double precision AS "Wind_direction_deg",
    NULL::double precision AS "Barometric_pressure_hPa",
    NULL::double precision AS "Dewpoint_C",
    NULL::double precision AS "Dewpoint_F",
    NULL::character varying AS appliance
   FROM co2_difference_hrly;
