# -*- coding: utf-8 -*-
import os
from shutil import copyfile
import argparse
import sys

usage_text = 'Use "manage.py config" to configure this application\n' \
             'Use "manage.py dbmigrate" to migrate database\n'

configs_path = 'configs'
manage_path = 'manage'
files_to_copy = ['config.py']


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        print(usage_text)
        sys.exit(2)


my_parser = MyParser()
my_parser.add_argument("pram")

args = my_parser.parse_args()

if args.pram == 'config':

    steps = 0

    print('Start the configuration ...')
    print('-' * 20)

    if not os.path.exists(configs_path):
        os.makedirs(configs_path)
        print(f'Created directory: {configs_path}')
        steps += 1

    dir_configs = os.listdir(configs_path)

    for file in files_to_copy:
        if file not in dir_configs:
            copyfile(f'{manage_path}/{file}', f'{configs_path}/{file}')
            print(f'Created file: {configs_path}/{file}')
            steps += 1

    if steps >= 1:
        print('-' * 20)

    print(f'Steps taken: {steps}')
    print('Successfully completed')

elif args.pram == 'dbmigrate':
    from db import *



    try:
        db.evolve()
    except Exception as e:
        print("ERROR IN CONNECTION",e)
        # return False

else:
    print(usage_text)
    sys.exit(2)
