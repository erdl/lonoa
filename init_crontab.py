import egauge.script.orm_egauge as orm_egauge
import configparser
import crontab
import numpy
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

    # create a list using a database query that selects each unique active script_folder that is not set to None
    script_folders = [stype[0] for stype in conn.query(orm_egauge.SensorInfo.script_folder). \
        filter(orm_egauge.SensorInfo.is_active == True).distinct() if stype[0]]
    print(__file__ + ': extracted active script folders', str(script_folders), 'from database')

    # create a list of the active script filenames to compare with commands in crontab
    # always include init_crontab.py, so it will schedule itself if missing
    database_active_scripts = ['init_crontab.py']
    for script_folder in script_folders:
        # use ".value" to access value of script_folder enum
        script_folder = script_folder.value
        # hobo has a different script name
        if script_folder == 'hobo':
            script_filename = 'extract_hobo.py'
        else:
            script_filename = 'api_' + script_folder + '.py'
        database_active_scripts.append(script_filename)

    crontab_active_scripts = []
    # go through all existing jobs to remove jobs not in list; also add active jobs already in crontab to list
    for job in cron:
        # convert job to string for comparison
        job_string = str(job)
        # compare job only if it contains project path and job is not commented out
        if (project_path in job_string) and (job_string[0] is not "#"):
            # extract script_filename from cron job string by splitting after python3 and before the next space
            script_filename = job_string.split('python3 ')[1].split()[0]
            if script_filename not in database_active_scripts:
                print(__file__ + ': removing job \"' + job_string + "\"")
                cron.remove(job)
                # update crontab with removal
                cron.write()
            else:
                crontab_active_scripts.append(script_filename)
    print(__file__ + ': jobs for', str(crontab_active_scripts), 'were already in crontab')

    # use numpy.setdiff1d() to get all active scripts in database list not in crontab list
    scripts_missing_from_crontab = numpy.setdiff1d(database_active_scripts, crontab_active_scripts)
    print(__file__ + ': jobs missing from crontab', scripts_missing_from_crontab)

    # add jobs for all active scripts missing from crontab
    for script_name in scripts_missing_from_crontab:
        # use if else statement since job is formatted differently if it is a sensor script vs. init_crontab.py
        if script_name != 'init_crontab.py':
            # sensor commands should cd to the appropriate */script directory, then run the script
            # and write outputs to crontab.txt in the */script directory
            script_folder = script_name.split('_')[1].split('.py')[0]
            job = cron.new(command='cd ' + project_path + '/' + script_folder + '/script && '
                                   + 'python3 ' + script_name + ' >> crontab.txt')
            # set sensor crontab job to run every five minutes
            job.minute.every(5)
        # schedule init_crontab job if not already scheduled
        else:
            job = cron.new(command='cd ' + project_path + '/ && python3 ' + str(script_name))
            # set init_crontab job to run every five minutes
            job.minute.every(5)
        print(__file__ + ': attempting to write ' + script_name + ' job to crontab')
        cron.write()

    # close database connection
    conn.close()
