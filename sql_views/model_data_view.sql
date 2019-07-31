-- join building energy usage model tables to view data
-- (energy usage based on model scenario and end use)
-- [used by NA]
CREATE VIEW model_data_view AS 

 SELECT model_scenarios.scenario_name,
    model_end_uses.end_use,
    model_end_uses.model_end_use_name,
    model_data.datetime,
    model_data.power_w
   FROM model_data
     JOIN model_scenarios ON model_data.scenario_id = model_scenarios.scenario_id
     JOIN model_end_uses ON model_data.end_use_id = model_end_uses.end_use_id;
