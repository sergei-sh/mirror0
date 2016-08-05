

import ConfigParser 
import time
import os.path
import sys

CONFIG_FILE = os.path.expandvars("$HOME/.mirror0/mirror0.ini")

#singleton config object
class Config:
    class ConfigLoader(ConfigParser.ConfigParser, object):
        def __init__(self):
            super(self.__class__, self).__init__()
            if 0 == len(self.read(CONFIG_FILE)):
                sys.exit('Need %s to run' % CONFIG_FILE)

    _config = ConfigLoader()
    _time = time.strftime("%H:%M %d %b")

    @staticmethod
    def value(section, key):
        val = os.path.expandvars(Config._config.get(section, key))
        if "log_directory" == key:
            val = os.path.join(val, Config._time)
        return val 

    def __call__(self):
        return Config._config

    
