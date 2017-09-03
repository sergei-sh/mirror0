""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: Concrete extractor for afl.com.au
"""

from logging import ERROR, INFO, WARNING, DEBUG

from mirror0.generic_spider import RawExtractorPipeline
from mirror0.generic_spider import Spider
from mirror0.sscommon.aux import log, format_exc
import re

import os.path
import mirror0

from mirror0 import Config

class AflExtractorPipeline(RawExtractorPipeline):

    _need_twitter = True

    def __init__(self):

        #self._idx_file = os.path.join(Config.value(mirror0.SECTION_COMMON, "log_directory"), "html.log")
        #with open(self._idx_file, "w") as f:
        #    f.write("Started")

        RawExtractorPipeline.__init__(self)

        self._title_x = "//div[@class='article']/div[@class='story-header']/h1/text()"
        self._text_paragraph_x = "//div[@class='article']/div[@class='story-content']/descendant::*/text()"
        self._text_paragraph_x += " | //div[@class='article']/div[@class='story-content']/text()"
        self._abstract_paragraph_x = None
        self._picture_x = "//div[@class='article']/img/@src | //div[@class='article']/*/img/@src | //div[@class='article']/*/*/img/@src | //div[@class='article']/*/*/*/img/@src | //div[@class='article']/*/*/*/*/img/@src"
        self._time_x = "//div[@class='article']/div/p/*[@class='pubdate']/text()"
        self._time_format_in = ["%B %d, %Y%I:%M %p", "%B %d, %Y %I:%M %p", "%I:%M%p %b %d, %Y"] # 11:17pm Mar 27, 2014]
        self._time_format_out = "%B %d, %Y %I:%M %p" 

    def _extract_more(self, item, spider):
        try:
            log("AflExtractor start %s" % item['title'], DEBUG)
            selector = item['raw_html']
            item['ooyala_video_ids'] = selector.xpath("//div[re:test(@class, 'ooyala-player')]/@data-content-id").extract()

            if item['ooyala_video_ids']:
                log("Matched %s" % item['raw_url'], DEBUG)
            else:
                log("Not matched %s" % item['raw_url'], DEBUG)
                #with open(self._idx_file, "a") as f:
                #     f.write(item['raw_text'] + "\n\n")
        
            if self._need_twitter:
                item['twitter_data'] = \
                    [re.search(r'status/(\d+)', twit_lnk).group(1) 
                        for twit_lnk in selector.xpath("//blockquote[@class='twitter-video']/a[re:test(@href, 'status/\d+')]/@href").extract()]

            return item
        except Exception as e:
            format_exc(self, "_extract_more", e)
