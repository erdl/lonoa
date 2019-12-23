import argparse
import orm
import configparser
import crontab
import numpy
import sqlalchemy


if __name__=='__main__':
    """
    1. get 'min' argument to set how often to run crontab job in minutes
    2. open lonoa crontab and connection to database named in config.txt
    3. get a list of all unique active script_folder types from sensor_info table in db
        4. use that to create a list of active script names, including init_crontab.py by default
    5. go through each uncommented job in crontab
        6. check all jobs that contain path of current project
            7. extract script filename from those jobs and check if filename is also in active script list
                8. remove jobs from crontab that are not in list
                9. if job was already in crontab list, add its script's filename to an active_crontab list
    10. compare active database script list with active crontab script list
        11. add any database script jobs to crontab that were not already there
    """
    # create parser that takes command line arguments
    parser = argparse.ArgumentParser(description='Update crontab with active lonoa jobs')
    # minute argument
    # run lonoa scripts every 30 minutes by default if no argument is given
    parser.add_argument('--min', type=int, default=30,
                        help='set how often to run lonoa crontab jobs in minutes')
    args = parser.parse_args()

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

    # create a list using a database query that selects each unique active script_folder that is not set to None
    script_folders = [stype[0] for stype in conn.query(orm.SensorInfo.script_folder). \
        filter(orm.SensorInfo.is_active == True).distinct() if stype[0]]
    print(__file__ + ': extracted active script folders', str(script_folders), 'from database')

    # create a list of the active script filenames to compare with jobs in crontab
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

    # get path of project to check and create lonoa crontab jobs
    project_path = conn.query(orm.Project.project_folder_path).first()[0]

    # list that will hold lonoa script names already in crontab
    crontab_active_scripts = []
    # go through all existing jobs to remove jobs not in list; also add active jobs already in crontab to list
    for job in cron:
        # convert job to string for comparison
        job_string = str(job)
        # compare job only if it contains project path and job is not commented out
        if (project_path in job_string) and (job_string[0] is not "#"):
            # extract script_filename from cron job string by splitting after python3 and before the next space
            script_filename = job_string.split('python3 ')[1].split()[0]
            # extract the interval of minutes when crontab runs
            script_minutes = int(job_string.split()[0].split('/')[1])
            # remove job from crontab if it is not active in database or if interval of minutes has been updated
            if script_filename not in database_active_scripts or script_minutes != args.min:
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
            # sensor cron job commands should cd to the appropriate */script directory, then run the script
            # and write outputs to crontab.txt in the */script directory
            script_folder = script_name.split('_')[1].split('.py')[0]
            job = cron.new(command='cd ' + project_path + '/' + script_folder + '/script && '
                                   + 'python3 ' + script_name)
        # schedule init_crontab job if not already scheduled
        else:
            job = cron.new(command='cd ' + project_path + '/ && python3 ' + str(script_name) + ' --min=' + str(args.min))
        # use --min argument to set run interval in minutes of sensor crontab job
        job.minute.every(args.min)
        print(__file__ + ': attempting to write ' + script_name + ' job to crontab')
        cron.write()

    # close database connection
    conn.close()
