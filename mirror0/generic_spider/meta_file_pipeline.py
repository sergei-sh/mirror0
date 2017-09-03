""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from logging import ERROR, INFO
import json
import os.path

from scrapy.exceptions import DropItem

from mirror0 import *
from mirror0.sscommon.aux import log, format_exc
from mirror0 import Config


class MetaFilePipeline(object):
    def process_item(self, item, spider):
        try:
            META_FILE = "meta.dat"
            file_path = os.path.join(item['path'], META_FILE)
            f = open(file_path, "w") 
            f.write("url=%s\n" % item['raw_url'])
            f.write("publishedUTC=%s\n" % item['time'])

            if "ooyala_video_ids" in item and item['ooyala_video_ids']:
                f.write("data-content-id=%s" % json.dumps(item['ooyala_video_ids'], separators=(", ", " ")))
        except Exception as e:
            format_exc(self, "process_item", e)
        finally:
            f.close()

        return item
        

