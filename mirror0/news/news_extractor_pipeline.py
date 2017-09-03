""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from logging import ERROR, INFO, WARNING, DEBUG

from mirror0.generic_spider import RawExtractorPipeline
from mirror0.generic_spider import Spider
from mirror0.sscommon.aux import log, format_exc
import re

import os.path
import mirror0

class NewsExtractorPipeline(RawExtractorPipeline):
    """XPaths/custom logic for item extraction specific to this website
    """

    def __init__(self):

        RawExtractorPipeline.__init__(self)

        self._title_x = """//div[@class='story-headline']/h1[@class='heading']/text() | \
        //div[@class='module-header vms-header']/h3[@class='heading']/text()"""

        self._text_paragraph_x = '//div[@class="story-body"]/descendant::p/descendant::text()'
        self._abstract_paragraph_x = None
        self._picture_x = '//div[@class="story-body"]/descendant::img/@src'
        self._time_x = ""
        self._time_format_in = ["%B %d, %Y%I:%M %p", "%B %d, %Y %I:%M %p", "%I:%M%p %b %d, %Y"] # 11:17pm Mar 27, 2014]
        self._time_format_out = "%B %d, %Y %I:%M %p" 

    def _extract_more(self, item, spider):
        try:
            log("NewsExtractor start %s" % item['title'], DEBUG)
            selector = item['raw_html']
            item['ooyala_id'] = selector.xpath("//div[re:test(@class, 'vms module')]/@vms-embedcode").extract_first()
            if item['ooyala_id']:
               log("Matched %s" % item['raw_url'], DEBUG)
            else:
                item['ooyala_id'] = "" 
                log("Not matched %s" % item['raw_url'], DEBUG)
        
            return item
        except Exception as e:
            format_exc(self, "_extract_more", e)
