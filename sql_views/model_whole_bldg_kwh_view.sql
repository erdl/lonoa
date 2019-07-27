-- grab whole building energy usage for a given scenario
-- [used by NA]
CREATE VIEW model_whole_bldg_kwh_view AS 

 SELECT model_scenarios.scenario_name,
    model_data.datetime,
    model_data.power_w / 1000::double precision AS "kWh"
   FROM model_data
     FULL JOIN model_scenarios ON model_data.scenario_id = model_scenarios.scenario_id
     FULL JOIN model_end_uses ON model_data.end_use_id = model_end_uses.end_use_id
  WHERE model_end_uses.end_use_id = 1;
