# Introduction

This project contain scripts that interact to the database project of ERDL. 

# Sensors 

 * HOBO 
 
# Setup
0. decide a \<directory\> to clone lonoa into and a \<database name\> and have your sensor data and webctrl user data ready
1. cd into \<directory\> and clone lonoa repo
   - ```git clone https://github.com/erdl/lonoa.git```
2. cd into repo
   - ```cd lonoa```
3. install python3 packages from requirements.txt
   - ```pip3 install -r requirements.txt```
4. run init_database.py
   - ```python3 init_database.py <database name>```
5. insert your webctrl username and password into api_authentication table
   - ```psql <database name> -c "INSERT INTO api_authentication(username,password) VALUES ('username','password')"```
6. import sensors into sensor_info table
   - ```psql my_init_db -c "\copy sensor_info from sensor_info.csv header csv"```
7. update sensor_info table
   - set script_folder column of sensors if not already set
      - ```psql my_init_db -c "UPDATE sensor_info SET script_folder='egauge' WHERE query_string LIKE 'egauge%'"```
      - ```psql my_init_db -c "UPDATE sensor_info SET script_folder='webctrl' WHERE query_string LIKE 'ABSPATH%'"```
   - set data_sensor_info_mapping (corresponding to column names in reading data csv) of egauge and hobo sensors
      - ```psql my_init_db -c "UPDATE sensor_info SET data_sensor_info_mapping='Usage [kW]' WHERE query_string LIKE 'egauge%'"```
   - set last_updated_datetime to (datetime of first reading - 1 minute)
      - ```psql my_init_db -c "UPDATE sensor_info SET last_updated_datetime=(TIMESTAMP '2019-07-31 23:59') WHERE script_folder='egauge' OR script_folder='webctrl'"```
      - when lonoa runs it pulls readings starting from (last_updated_datetime + 1 minute)
   - set active sensors to is_active=True
      - ```psql my_init_db -c "UPDATE sensor_info SET is_active=True WHERE script_folder='webctrl' OR script_folder='egauge'"```
7. run init_crontab.py
   - ```python3 init_crontab.py```
   