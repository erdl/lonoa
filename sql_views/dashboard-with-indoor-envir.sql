-- union of "kat".dashboard-union_individual and view-indoor-envir 
-- [used by dashbd_indoorenv_sched]
CREATE VIEW "dashboard-with-indoor-envir" AS 

 SELECT "dashboard-union_individual".datetime,
    "dashboard-union_individual".building,
    'Power-avg (kw)'::character varying AS type,
    "dashboard-union_individual".appliance,
    NULL::character varying AS room,
    NULL::character varying AS surface,
    NULL::double precision AS "Humidity (%)",
    NULL::double precision AS "Temperature (F)",
    NULL::double precision AS "Light (lux)",
    NULL::double precision AS "CO2 (ppm)",
    NULL::double precision AS "Window",
    "dashboard-union_individual"."Power Avg (kW)"
   FROM kat."dashboard-union_individual"
UNION
 SELECT "view-indoor-envir".datetime,
    "view-indoor-envir".building,
    "view-indoor-envir".type,
    NULL::character varying AS appliance,
    "view-indoor-envir".room,
    "view-indoor-envir".surface,
    "view-indoor-envir"."Humidity (%)",
    "view-indoor-envir"."Temperature (F)",
    "view-indoor-envir"."Light (lux)",
    "view-indoor-envir"."CO2 (ppm)",
    "view-indoor-envir"."Window",
    NULL::double precision AS "Power Avg (kW)"
   FROM "view-indoor-envir";
