import egauge.script.orm_egauge
import getpass #used to get username
import os
import sqlalchemy
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

        # write database name to config file
        config_path = project_folder_path + '/' + 'config.txt'
        with open(config_path, 'w+') as file:
            config_string = 'db = ' + db_name
            print(__file__ + ': writing \'' + config_string + '\' to config.txt')
            file.write(config_string)

        # create database and create a database user based on the user that ran the script
        current_user = getpass.getuser()
        # connect to database 'postgres' as current user
        engine = sqlalchemy.create_engine('postgres://' + current_user + '@/postgres')
        conn = engine.connect()
        conn.execute('commit')
        # check if database already exists
        results = conn.execute('SELECT 1 FROM pg_database WHERE datname = \'' + db_name + '\'')
        # create database if not exists
        if not results.first():
            print(__file__ + ': creating database ' + db_name)
            conn.execute('CREATE DATABASE ' + db_name)
        else:
            print(__file__ + ': database named ' + sys.argv[1] + ' already exists')
        conn.close()

        # create all necessary tables in database
        print(__file__ + ': creating tables in database ' + db_name)
        egauge.script.orm_egauge.setup()

        # connect to the created database to add project_folder_path to Project table
        db_url = "postgresql:///" + db_name
        db = sqlalchemy.create_engine(db_url)
        Session = sqlalchemy.orm.sessionmaker(db)
        conn = Session()
        project_folder_path = os.getcwd()
        # check if project_folder_path exists already
        results = conn.execute('SELECT 1 FROM project WHERE project_folder_path = \'' + project_folder_path + '\'')
        if not results.first():
            project_row = egauge.script.orm_egauge.Project(project_folder_path=project_folder_path)
            conn.add(project_row)
        else:
            print(__file__ + ': project_folder_path ' + project_folder_path + ' already exists in project table')
        conn.commit()
        conn.close()

    except TypeError as exception:
        print('Usage: \'' + 'python3 ' + sys.argv[0] + ' <database name>\'')
