# from sqlalchemy import create_engine

# from pathlib import Path #used to read config.txt in parent directory

# import configparser
import egauge.script.orm_egauge #as orm_egauge # how to import modules in nested py files
import getpass #used to get username
import os
# import pathlib
import sqlalchemy
import subprocess
import sys


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise TypeError

        db_name = sys.argv[1]

        # The Linux user that will run api_...py and extract_...py scripts from the crontab
        # Grant database and file permissions to this user.
        locked_username = 'locked_user'

        # make sure working directory = parent directory of this file, then get full project folder path
        parent_directory = os.path.abspath(os.path.join(__file__, os.pardir))
        os.chdir(parent_directory)
        project_folder_path = os.getcwd()

        #write database name to config file
        config_path = project_folder_path + '/' + 'config.txt'
        with open(config_path, 'w+') as file:
            config_string = 'db = ' + db_name
            print(__file__ + ': writing \'' + config_string + '\' to config.txt')
            file.write(config_string)

        # create database and create a database user based on the user that ran the script
        current_user = getpass.getuser()
        # connect to database 'postgres' as current user
        # TODO should we assume that current_user has database access?
        engine = sqlalchemy.create_engine('postgres://' + current_user + '@/postgres')
        conn = engine.connect()
        conn.execute('commit')
        #check if database already exists
        results = conn.execute('SELECT 1 FROM pg_database WHERE datname = \'' + db_name + '\'')
        #create database if not exists
        if not results.first():
            print(__file__ + ': creating database ' + db_name)
            conn.execute('CREATE DATABASE ' + db_name)
        else:
            print(__file__ + ': database named ' + sys.argv[1] + ' already exists')
        # grant database permissions to root and locked user
        #users = [locked_username, 'root']
        #for user in users:
            # create database role for crontab user if not exists
            #results = conn.execute('SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = \'' + user +'\'')
            #if not results.first():
            #    conn.execute('CREATE USER ' + user)
            #else:
            #    print(__file__ + ': database user named ' + user + ' already exists')
            ##allow user to connect to database
            #conn.execute('GRANT CONNECT ON DATABASE ' + db_name + ' TO ' + user);
            #conn.execute('commit')
        conn.close()

        # create all necessary tables in database
        print(__file__ + ': creating tables in database ' + db_name)
        egauge.script.orm_egauge.setup()

        # grant database permissions to root and locked_user
        # get current linux user
        current_user = getpass.getuser()
        # connect to database as current linux user
        engine = sqlalchemy.create_engine('postgres://' + current_user + '@/' + db_name)
        conn = engine.connect()
        conn.execute('commit')
        ## grant db permissions to locked user and root
        #users = [locked_username, 'root']
        #for user in users:
            ## grant all necessary database privileges for crontab user to run scripts from crontab
            #conn.execute('GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO ' + user)
            #conn.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ' + user)
        conn.close()

        # add project_folder_path to Project table
        db_url = "postgresql:///" + db_name
        db = sqlalchemy.create_engine(db_url)
        Session = sqlalchemy.orm.sessionmaker(db)
        conn = Session()
        project_folder_path = os.getcwd()
        #check if project_folder_path exists already
        results = conn.execute('SELECT 1 FROM project WHERE project_folder_path = \'' + project_folder_path + '\'')
        if not results.first():
            project_row = egauge.script.orm_egauge.Project(project_folder_path=project_folder_path)
            conn.add(project_row)
        else:
            print(__file__ + ': project_folder_path ' + project_folder_path + ' already exists in project table')
        conn.commit()
        conn.close()

        #print(__file__ + ': enabling file permissions')
        ## create sensors group for sensors file permissions
        #subprocess.run(['sudo', 'groupadd', 'sensors'])
        ## make sensors primary group of current user
        #subprocess.run(['sudo', 'usermod', '-g', 'sensors', current_user])
        #subprocess.run(['sudo', 'usermod', '-g', 'sensors', locked_username])
        ## add locked user to sensors
        ## subprocess.run(['sudo', 'usermod', '-a', '-G', 'sensors', 'locked_user'])

        ## grant read, write permissions to locked_user
        #sensor_types = ('egauge', 'hobo', 'webctrl')
        # go through each relevant subfolder in sensors
        #for sensor_type in sensor_types:
            #filename = project_folder_path + '/' + sensor_type + '/script/error.log'
            # should create error_log file if it does not already exist
            #with open(filename, 'a+') as file:
                ## use subprocess to run setfacl Linux command similar to "setfacl -m user:locked_user:rw egauge/script/error.log"
                ## should grant read and write permissions for error.log file to user
                #subprocess.run(['setfacl', '-m', 'user:' + locked_username + ':rw', filename])
            ## grant file permissions on sensor_type/script/ directories so that locked_user can write using crontab
            #subprocess.run(['sudo', 'chgrp', 'sensors', sensor_type + '/script'])

        # TODO if needed, grant execute file permissions on api/extract/orm scripts to locked_user


    except TypeError as exception:
        print('Usage: \'' + 'python3 ' + sys.argv[0] + ' <database name>\'')
    # except (sqlalchemy.exc.OperationalError, IndexError) as exception:
    #     print(__file__, exception.__class__.__name__ + ': Usage: \'' + 'python3 ' + sys.argv[0] + ' <database name>\'')
    # except:
    #     print("Unexpected error:", sys.exc_info()[0])
