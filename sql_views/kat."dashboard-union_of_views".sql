-- This view does not work properly
-- "ERROR:  failed to find conversion function from unknown to character varying"
create view kat."dashboard-union_of_views" as

 select "dashboard-plugloads".building,
    "dashboard-plugloads".appliance,
    "dashboard-plugloads".datetime,
    "dashboard-plugloads"."Power Avg (kW)"
   from kat."dashboard-plugloads"
union
 select "dashboard-indoor_lights".building,
    "dashboard-indoor_lights".appliance,
    "dashboard-indoor_lights".datetime,
    "dashboard-indoor_lights"."Power Avg (kW)"
   from kat."dashboard-indoor_lights"
union
 select "dashboard-hvac".building,
    "dashboard-hvac".appliance,
    "dashboard-hvac".datetime,
    "dashboard-hvac"."Power Avg (kW)"
   from kat."dashboard-hvac"
union
 select "dashboard-fans_and_outdoor_lights".building,
    "dashboard-fans_and_outdoor_lights".appliance,
    "dashboard-fans_and_outdoor_lights".datetime,
    "dashboard-fans_and_outdoor_lights"."Power Avg (kW)"
   from kat."dashboard-fans_and_outdoor_lights"
union
 select "dashboard-pv".building,
    "dashboard-pv".appliance,
    "dashboard-pv".datetime,
    "dashboard-pv"."Power Avg (kW)"
   from kat."dashboard-pv"
union
 select "dashboard-whole-building-use".building,
    "dashboard-whole-building-use".appliance,
    "dashboard-whole-building-use".datetime,
    "dashboard-whole-building-use"."Power Avg (kW)"
   from kat."dashboard-whole-building-use"
  order by 3, 1;
