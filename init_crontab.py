import egauge.script.orm_egauge as orm_egauge
import configparser
import crontab
import sqlalchemy


if __name__=='__main__':
    #create a cron object; requires sudo if user running script is not lonoa
    cron = crontab.CronTab(user='lonoa')

    # get db connection
    config_path = "config.txt"
    with open(config_path, "r") as file:
        # prepend '[DEFAULT]\n' since ConfigParser requires section headers in config files
        config_string = '[DEFAULT]\n' + file.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    db_url = "postgresql:///" + config['DEFAULT']['db']
    db = sqlalchemy.create_engine(db_url)
    Session = sqlalchemy.orm.sessionmaker(db)
    conn = Session()

    # get path of project for usage in crontab commands
    project_path = conn.query(orm_egauge.Project.project_folder_path).first()[0]

    # go through all existing jobs
    for job in cron:
        # convert job to string for comparison
        job_string = str(job)
        # remove job if job command contains project path and job is not commented out
        if (project_path in job_string) and (job_string[0] is not "#"):
            print(__file__ + ': removing job \"' + job_string + "\"")
            cron.remove(job)
            # update crontab with removal
            cron.write()

    # create a list with each unique sensor type
    sensor_types = [stype[0] for stype in conn.query(orm_egauge.SensorInfo.sensor_type).filter(orm_egauge.SensorInfo.is_active==True).distinct()]
    print(__file__ + ': extracted active sensor types ', str(sensor_types), ' from database')

    for sensor_type in sensor_types:
        # hobo has a different script name
        if sensor_type == 'hobo':
            sensor_scriptname = 'extract_hobo.py'
        else:
            sensor_scriptname = 'api_' + sensor_type + '.py'

        # command should cd to the appropriate */script directory, then run the script
        # and write outputs to crontab.txt in the */script directory
        job = cron.new(command='cd ' + project_path + '/' + sensor_type + '/script && ' + \
                               'python3 ' + sensor_scriptname + ' >> crontab.txt')

        # set crontab jobs to run every five minutes
        job.minute.every(5)
        print(__file__ + ': attempting to write ' + sensor_type + ' job to crontab')
        cron.write()

    conn.close()
