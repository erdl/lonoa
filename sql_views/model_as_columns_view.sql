-- get energy usage for different models and end uses displayed in multiple columns
-- [used by NA]
CREATE VIEW model_as_columns_view AS 

 SELECT 'model' AS building_id,
    model_data.datetime,
    max(
        CASE
            WHEN model_scenarios.scenario_id = 4 THEN model_data.power_w / 1000::double precision
            ELSE NULL::double precision
        END) AS "AC_77_kWh",
    max(
        CASE
            WHEN model_scenarios.scenario_id = 3 THEN model_data.power_w / 1000::double precision
            ELSE NULL::double precision
        END) AS "AC_80_kWh",
    max(
        CASE
            WHEN model_scenarios.scenario_id = 5 THEN model_data.power_w / 1000::double precision
            ELSE NULL::double precision
        END) AS "MM_kWh",
    max(
        CASE
            WHEN model_scenarios.scenario_id = 1 THEN model_data.power_w / 1000::double precision
            ELSE NULL::double precision
        END) AS "NV_24_kWh",
    max(
        CASE
            WHEN model_scenarios.scenario_id = 2 THEN model_data.power_w / 1000::double precision
            ELSE NULL::double precision
        END) AS "NV Occ_kWh",
    max(
        CASE
            WHEN model_scenarios.scenario_id = 6 THEN model_data.power_w / 1000::double precision
            ELSE NULL::double precision
        END) AS "AC_77_IECC_base_kWh"
   FROM model_data
     FULL JOIN model_scenarios ON model_data.scenario_id = model_scenarios.scenario_id
     FULL JOIN model_end_uses ON model_data.end_use_id = model_end_uses.end_use_id
  WHERE model_end_uses.end_use_id = 1
  GROUP BY model_scenarios.scenario_name, model_data.datetime;
