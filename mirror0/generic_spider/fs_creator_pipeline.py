""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from distutils import dir_util
import functools
from logging import ERROR, WARNING, DEBUG
import os
import os.path
import shutil

from scrapy.exceptions import DropItem

from mirror0 import *
from mirror0.sscommon.aux import log, format_exc
from mirror0 import Config

config_out = Config.value(SECTION_COMMON, "output_directory")

class FSCreatorPipeline(object):

    __vlog_dir = ""

    def __init__(self):
        self._top_dir = ""

    def _create_more(self, item, spider):
        return item

    def process_item(self, item, spider):
        try:
            log("FSCreator start %s" % item['title'], DEBUG)
            #log("fs for %s" % item['title'])
            item_dir = os.path.join(self._top_dir, self.__class__.getItemDir(item, spider))
            if os.path.isdir(item_dir):
                log("Article path exists, overwriting: %s" % item_dir, DEBUG)
            try:
                dir_util.mkpath(item_dir)
            except Exception as e:
                log("Can't create article directory %s : %s" % (item_dir, str(e)), ERROR)
            
            item['path'] = item_dir

            if not self.__vlog_dir:
                self.__vlog_dir = os.path.join(Config.value(SECTION_COMMON, "log_directory"), spider.name + "_streaming")
                shutil.rmtree(self.__vlog_dir, True)
                try:
                    os.mkdir(self.__vlog_dir)
                except OSError as e:
                    pass
                self.__need_clean = False

            logfile_path = os.path.join(self.__vlog_dir, item['title'] + ".log")

            class VideoLog:
                def __init__(self):
                    self.logfile_path = None

            vlog = VideoLog()
            vlog.file_path = logfile_path
            vlog.__call__ = functools.partial(FSCreatorPipeline.append_file, logfile_path) 
            item['vlog'] = vlog 

            return self._create_more(item, spider)
        except Exception as e:
            if type(e) == DropItem:
                raise
            else:
                format_exc(self, "process_item", e)

    def open_spider(self, spider):
        self._top_dir = os.path.join(config_out, 
            spider.allowed_domains[0])
        try:
            dir_util.mkpath(self._top_dir)
        except Exception as e:
            log("Can't create output directory %s : %s" % (self._top_dir, str(e)), ERROR)

    @staticmethod
    def append_file(file_path, text):
        #print "writing to %s" % file_path
        with open(file_path, "a") as f:
            f.write(text + "\n")
        
