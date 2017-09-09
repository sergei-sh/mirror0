
from distutils import dir_util
import logging

def init_logging():
    """ Initializes project logging and creates LOGS directory if necessary
    """
    logdir = Config.value(mirror0.SECTION_COMMON, "log_directory")
    dir_util.mkpath(logdir)
    fh = logging.FileHandler(os.path.join(logdir, "console.log"))
    fh.setFormatter(logging.Formatter("(%(module)s.%(funcName)s) [%(levelname)s]: %(message)s"))
    fh.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(fh)
