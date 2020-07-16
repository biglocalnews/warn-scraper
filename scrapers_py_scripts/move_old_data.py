#!/usr/bin/python
import requests as req
from pathlib import Path
import os
import shutil
from datetime import date

def move_data():

    today_date = date.today()
    start_path = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/data/'
    end_path = '/Users/dilcia_mercedes/Big_Local_News/prog/WARN/old_data/'

    dirs = os.listdir(start_path)
    for file in dirs:
        full_start_path = f'{start_path}{file}'
        full_end_path = f'{end_path}{today_date}_{file}'
        print(full_start_path)
        shutil.move(full_start_path, full_end_path)

if __name__ == '__main__':
    move_data()




