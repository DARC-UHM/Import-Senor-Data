import errno
import json
import os


class ConfigFileHandler:
    def __init__(self):
        self.save_path = ''
        self.config = {}

        self.get_save_path()
        self.load_config()

    def get_save_path(self):
        if os.name == 'nt':
            self.save_path = os.getenv('LOCALAPPDATA')
        else:
            self.save_path = os.getenv('HOME') + '/Library/Application Support'

    def load_config(self):
        os.chdir(self.save_path)
        try:
            os.mkdir('CTDProcess')
        except OSError as err:
            if err.errno != errno.EEXIST:
                # if the OS error is something other than 'directory already exists', raise the error
                raise
            # otherwise, ignore the error
            pass
        os.chdir('CTDProcess')
        try:
            with open('ctd_process_config.json', 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            self.load_default_config()

    def load_default_config(self):
        self.config = {
            'cruise_number': '',
            'base_dir': '/Volumes/maxarray2/varsadditional',
            'output_dir': '/Volumes/maxarray2/varsadditional',
            'ctd_dir': '${base_dir}/CTD',
            'tracking_dir': '${base_dir}/Tracking',
            'ctd_file_names': '${cruise}_${dive}_',
            'tracking_file_names': '${cruise}_${dive}_RovTrack1Hz.csv',
            'ctd_cols': {
                'timestamp': 1,
                'temperature': 4,
                'depth': 10,
                'salinity': 11,
                'oxygen': 13
            },
            'tracking_cols': {
                'unix_time': 3,
                'altitude': 5,
                'latitude': 6,
                'longitude': 7
            }
        }

    def save_config(self, new_config):
        os.chdir(self.save_path)
        try:
            os.mkdir('CTDProcess')
        except OSError as err:
            if err.errno != errno.EEXIST:
                print(err)
                return False
        os.chdir('CTDProcess')
        try:
            with open('ctd_process_config.json', 'w') as config_file:
                json.dump(new_config, config_file, indent=2)
        except IOError as err:
            print(err)
            return False
        return True
