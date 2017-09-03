""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: This should be rewritten actually. Blocking code urlopen() in the twisted callback.
"""

from logging import ERROR, DEBUG
import os.path
import urllib2

from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

from mirror0 import *
from mirror0.sscommon.aux import log, format_exc
from mirror0 import Config

NO_PICTURES = False

ARTICLE_FILE = "article.txt"

class TextImagePipeline(object):
    """Downloads files using previously scraped URL, being stored in the item"""
    STATE_ID = "T&IMG"
    NAME = "text_image_pipeline"

    def process_item(self, item, spider):
        if self.NAME in spider.disabled_pipelines:
            return item 

        log("TextImage pipeline {0}".format(item['raw_url']))
        try:
            spider.start_state(item['raw_url'], TextImagePipeline.STATE_ID)
            
            text_path = os.path.join(item['path'], ARTICLE_FILE) 
            if item['text']:
                with open(text_path, "w") as f:
                    f.write(item['text'])
        except Exception as e:
            log("Error writing article text %s : %s" % (item['raw_url'], str(e)), ERROR)

        picture_timeout = get_project_settings().get('DOWNLOAD_TIMEOUT', 30)

        if item['pictures']:
            log("Downloading images for {0}".format(item['raw_url']), DEBUG)
        i = 0
        for img in item['pictures']:
            try:
                (foo, ext) = os.path.splitext(img)
                img_name = "%02i" % i + (ext if ext else "")
                img_path = os.path.join(item['path'], img_name) 
                if "/" == img[0]:
                    img = os.path.join(spider.BASE_URL, img[1:])

                if not NO_PICTURES:
                    fileobj = urllib2.urlopen(img, timeout=picture_timeout)
                    with open(img_path, "wb") as f:
                        f.write(fileobj.read())
                i += 1

            except Exception as e:
                 log("Error writing article image %s : %s" % (img, str(e)), ERROR)     
        if i:
             log("%i images retrieved for %s" % (i, item['title']), DEBUG)
                
        spider.finalize_state(item['raw_url'], TextImagePipeline.STATE_ID)
        return item
 
