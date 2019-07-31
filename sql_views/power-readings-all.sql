-- union of power-readings-only and calc-other-inst-power
-- [used by NA]
CREATE VIEW "power-readings-all" AS 

 SELECT "power-readings-only".datetime,
    "power-readings-only".units,
    "power-readings-only".building,
    "power-readings-only".variable_name,
    "power-readings-only".type,
    "power-readings-only".appliance,
    "power-readings-only"."Power avg (kW)",
    "power-readings-only"."Power instantaneous (kW)"
   FROM "power-readings-only"
UNION ALL
 SELECT "calc-other-inst-power".datetime,
    "calc-other-inst-power".units,
    "calc-other-inst-power".building,
    "calc-other-inst-power".variable_name,
    "calc-other-inst-power".type,
    "calc-other-inst-power".appliance,
    "calc-other-inst-power"."Power avg (kW)",
    "calc-other-inst-power"."Power instantaneous (kW)"
   FROM "calc-other-inst-power";
