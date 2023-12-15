import errno
import json
import os


class ConfigFileHandler:
    def __init__(self):
        self.save_path = ''
        self.config = {}

        self.get_save_path()
        self.load_config()
        print(self.save_path)
        print(self.config)

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
            'cruiseNum': '',
            'baseDir': '/Volumes/maxarray2/varsadditional',
            'outputDir': '/Volumes/maxarray2/varsadditional',
            'ctdDirPath': '${base_dir}/CTD',
            'trackingDirPath': '${base_dir}/Tracking',
            'ctdFileName': '${cruise}_${dive}_',
            'trackingFileName': '${cruise}_${dive}_RovTrack1Hz.csv',
            'ctdColumns': {
                'timestamp': 1,
                'temperature': 4,
                'depth': 10,
                'salinity': 11,
                'oxygen': 13
            },
            'trackingColumns': {
                'unixTime': 3,
                'altitude': 5,
                'latitude': 6,
                'longitude': 7
            }
        }

    def save_config(self, new_config):
        pass
