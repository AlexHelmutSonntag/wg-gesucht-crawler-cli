import os
import sys
import json
import click
from .create_results_folders import create_folders
from .logger import get_logger
from . import user_details as user
from . import wg_gesucht

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN_INFO_FILE = os.path.join(BASE_DIR, '.data_files', 'login_info.json')


@click.command()
@click.option('--change-email', is_flag=True, help='Change your saved email address')
@click.option('--change-password', is_flag=True, help='Change your saved password')
@click.option('--change-phone', is_flag=True, help='Change your saved phone number')
@click.option('--change-all', is_flag=True, help='Change all you saved user details')
@click.option('--no-save', is_flag=True, help="The script won't save your wg-gesucht login details for future use")
def cli(change_email, change_password, change_phone, change_all, no_save):
    home_path = 'HOMEPATH' if sys.platform == 'win32' else 'HOME'
    dirname = os.path.join(os.environ[home_path], 'Documents', 'WG Finder')
    wg_ad_links = os.path.join(dirname, "WG Ad Links")
    offline_ad_links = os.path.join(dirname, "Offline Ad Links")
    logs_folder = os.path.join(dirname, 'logs')

    if not os.path.exists(logs_folder):
        os.makedirs(os.path.join(dirname, 'logs'))
    if not os.path.exists(os.path.join(BASE_DIR, '.data_files')):
        os.makedirs(os.path.join(BASE_DIR, '.data_files'))

    if not os.path.exists(wg_ad_links) or not os.path.exists(offline_ad_links) or not os.path.exists(logs_folder):
        create_folders(dirname, logs_folder)

    logger = get_logger(__name__, folder=logs_folder)
    login_info = dict()
    if os.path.isfile(LOGIN_INFO_FILE):
        with open(LOGIN_INFO_FILE) as file:
            login_info = json.load(file)

    login_info_changed = False
    if change_all or not login_info.get('email', '') or not login_info.get('password', ''):
        login_info = user.change_all()
        login_info_changed = True

    if change_email:
        login_info['email'] = user.change_email()
        login_info_changed = True

    if change_password:
        login_info['password'] = user.change_password()
        login_info_changed = True

    if change_phone:
        login_info['phone'] = user.change_phone()
        login_info_changed = True

    if login_info_changed and not no_save:
        user.save_details(LOGIN_INFO_FILE, login_info)
        logger.info('User login details saved to file')

    wg_gesucht.start_searching(
        login_info, wg_ad_links, offline_ad_links, logs_folder)
