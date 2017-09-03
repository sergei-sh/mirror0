""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: FS creation for afl.com.au
"""

import os.path

from mirror0.generic_spider import FSCreatorPipeline
from mirror0.sscommon.aux import url_path

class AflFSPipeline(FSCreatorPipeline):
    def __init__(self):
        super(AflFSPipeline, self).__init__()
        self._vlog_dir = None
 
    @staticmethod
    def getItemDir(item, spider):
        updir = url_path(spider.start_url)
        item_dir = os.path.join(updir.replace("/", "_"), item['title'])
        return item_dir




