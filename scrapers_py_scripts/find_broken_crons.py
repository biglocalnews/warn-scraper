import os

def broken_crons():

    list_files = ['california_warn_raw.csv', 'arizona_warn_raw.csv', 'alabama_warn_raw.csv', 'washington_warn_raw.csv', 'rhodeisland_warn_raw.csv', 'tennessee_warn_raw.csv', 'wisconsin_warn_raw.csv', 'florida_warn_raw.csv', 'michigan_warn_raw.csv', 'missouri_warn_raw.csv', 'kansas_warn_raw.csv', 'ohio_warn_raw.csv', 'oregon_warn_raw.csv', 'indiana_warn_raw.csv', 'newjersey_warn_raw.csv', 'oklahoma_warn_raw.csv', 'districtcolumbia_warn_raw.csv', 'maryland_warn_raw.csv', 'delaware_warn_raw.csv', 'nebraska_warn_raw.csv', 'southdakota_warn_raw.csv', 'newyork_warn_raw.csv', 'utah_warn_raw.csv']

    todays_files = []
    list_missing = []

    dir_path = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data'
    the_dir = os.listdir(dir_path)

    for file_name in the_dir:
        todays_files.append(file_name)

    for single_file in list_files:
        if single_file not in todays_files:
            list_missing.append(single_file)

    # print(list_missing)



    out_file = '/Users/dilcia_mercedes/Desktop/WARN_report.txt'

    with open(out_file, 'w') as the_file:
        the_file.write(str(list_missing))




if __name__ == '__main__':
    broken_crons()