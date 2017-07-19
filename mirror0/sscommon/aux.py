
import sys
import os.path
import logging
#TODO: uncomment
#import urlparse

def format_exc(self, method, exc):  
    fname = "" 
    lineno = 0 
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lineno = exc_tb.tb_lineno
    except:
        pass
    #print(exc_type, fname, exc_tb.tb_lineno)
    log("%s.%s : %s" % (self.__class__.__name__, method, str(exc_type.__name__) + ": " + str(exc)), logging.ERROR)
    log("file: %s line: %i" % (fname, lineno), logging.ERROR)
    log(r"/\\", logging.ERROR)

def log(msg, level = logging.INFO):
    #logging.getLogger("console").log(level, msg)
    logging.getLogger().log(level, msg)

def url_path(url):
    #o = urlparse.urlparse(url)
    return o.path[1:]

