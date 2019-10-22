# Introduction

This project contain scripts that interact to the database project of ERDL. 

# Sensors 

Currently, lonoa supports the following sensors:

 * HOBO 
 * Egauge
 * Webctrl 
 
# Setup

0. manually create lonoa user on the server (only needed for the first lonoa installation on the server)
1. switch to the lonoa user
   - ```su lonoa```
2. go to lonoa home directory and have your sensor and webctrl user ready
   - ```cd```
3. cd into lonoa home directory  and clone lonoa repo. The folder name will be the project name. 
   - ```git clone https://github.com/erdl/lonoa.git <project folder name>```
4. cd into repo
   - ```cd <project folder name>```
5. install python3 packages from requirements.txt (only needed for the first lonoa installation on the server)
   - ```sudo pip3 install -r requirements.txt```
6. manually create lonoa user on the database (only needed for the first lonoa installation on the server)
   - ```CREATE USER lonoa WITH CREATEDB```
7. run init_database.py
   - ```python3 init_database.py <database name>```
8. insert the webctrl username and password into api_authentication table
   - ```psql <database name> -c "INSERT INTO api_authentication(username,password) VALUES ('<apiusername>','<apipassword>')"```
9. import sensors into sensor_info table (An explanation of how to fill this table is provided in the next section below)
   - ```psql <database name> -c "\copy sensor_info from <csv filename> header csv"```
10. run init_crontab.py
   - ```python3 init_crontab.py```
  

# Sensor Info Table (Step 9) 

Examples adding new active sensors
- adding an egauge purpose
   - ```psql <database name> -c "insert into sensor_info(purpose_id, query_string, script_folder, unit, data_sensor_info_mapping, is_active, last_updated_datetime)values(<purpose_id>, '<query_string>', 'egauge', '<unit>', '<data_sensor_info_mapping>', True, ('<YYYY-MM-DD hh:mm>'));"```
- adding a webctrl purpose
   - ```psql <database name> -c "insert into sensor_info(purpose_id, query_string, script_folder, unit, is_active, last_updated_datetime) values(<purpose_id>, '<query_string>', 'webctrl', '<unit>', True, ('<YYYY-MM-DD hh:mm>'));"```
- adding a hobo purpose
   - ```psql <database name> -c "insert into sensor_info(purpose_id, query_string, script_folder, unit, data_sensor_info_mapping, is_active, last_updated_datetime) values(<purpose_id>, '<query_string>', 'hobo', '<unit>', '<data_sensor_info_mapping>', True, ('<YYYY-MM-DD hh:mm>'));"```

- exporting a table to csv
   -```psql <database name> -c "\copy <table_name> to <csv filename> header csv"```

Examples updating sensor_info
- set script_folder column of sensors if not already set
  - ```psql <database name> -c "update sensor_info set script_folder='egauge' where query_string like 'egauge%'"```
  - ```psql <database name> -c "update sensor_info set script_folder='webctrl' where query_string like 'ABSPATH%'"```
- set data_sensor_info_mapping (corresponding to column names in reading data csv of egauge)
  - ```psql <database name> -c "update sensor_info set data_sensor_info_mapping='<column name>' where query_string like 'egauge%'"```
- example setting last_updated_datetime for webctrl and egauge; remember to set to (datetime of first reading - 1 minute)
  - ```psql <database name> -c "update sensor_info set last_updated_datetime=('2019-07-31 23:59') where script_folder='egauge' or script_folder='webctrl'"```
  - when lonoa runs it pulls readings starting from (last_updated_datetime + 1 minute)
- set webctrl and egauge active sensors to is_active=True
  - ```psql <database name> -c "update sensor_info set is_active=True where script_folder='webctrl' or script_folder='egauge'"```