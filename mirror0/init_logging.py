""" 
Updated: 2017
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: Thinks how to avoid relative imports. Importing mirror0 causes cyclic dependency.
"""

from distutils import dir_util
import logging
import os

from .sscommon import Config
from . import SECTION_COMMON

def init_logging():
    """ Initializes project logging and creates LOGS directory if necessary
        
        raises: distutils.errors.DistutilsFileError
    """
    logdir = Config.value(SECTION_COMMON, "log_directory")
    dir_util.mkpath(logdir)
    fh = logging.FileHandler(os.path.join(logdir, "console.log"))
    fh.setFormatter(logging.Formatter("(%(module)s.%(funcName)s) [%(levelname)s]: %(message)s"))
    fh.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(fh)


