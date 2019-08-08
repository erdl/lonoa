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
   - ```psql my_init_db -c "\copy sensor_info from example_sensor_info.csv header csv"```
10. run init_crontab.py
   - ```python3 init_crontab.py```
  

# Sensor Info Table (Step 9) 
