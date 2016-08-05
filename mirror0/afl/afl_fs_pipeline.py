
import os.path

from mirror0.generic_spider import FSCreatorPipeline
from mirror0.sscommon.aux import url_path
#from mirror0 import Config
#from mirror0 import *


class AflFSPipeline(FSCreatorPipeline):
    def __init__(self):
        super(AflFSPipeline, self).__init__()
        self._vlog_dir = None
 
    @staticmethod
    def getItemDir(item, spider):
        updir = url_path(spider.start_url)
        item_dir = os.path.join(updir.replace("/", "_"), item['title'])
        return item_dir




