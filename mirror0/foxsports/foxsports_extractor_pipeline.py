""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from logging import ERROR, INFO, WARNING, DEBUG
from mirror0.sscommon.aux import log, format_exc
import re

from mirror0.generic_spider import RawExtractorPipeline

class FoxsportsExtractorPipeline(RawExtractorPipeline):
    """XPaths/custom logic for item extraction specific to this website
    """

    def __init__(self):
        RawExtractorPipeline.__init__(self)

        self._title_x = "//article/header[@class='article-header']/h1/text()"
        self._text_paragraph_x = "//article/div[@class='article-body']/descendant::p/text()"
        self._abstract_paragraph_x = ""
        self._picture_x = "//article/div[@class='article-body']/figure/img/@src | //article/header/div/div/figure/img/@src"
        #livepost pictures
        #self._picture_x += " | //article/div[@id='content-livepost']/div/div/figure/img/@src"
        self._time_x = "//meta[@property='article:published_time']/@content"
        self._time_format_in = []
        self._time_format_out = "%B %d, %Y, %I:%M %p" 

    def _extract_more(self, item, spider):
            try:
                selector = item['raw_html']

                if spider.NORMAL == spider.mode:
                    item['video_urls'] = selector.xpath("//video/source[@type='video/mp4']/@src").extract()
                elif spider.VIDEO == spider.mode:
                    pass
                else:
                    assert "Wrong mode value"

                #['https://snappytv-a.akamaihd.net/video/928000/603p603/2016-06-04T12-05-17.467Z--35.797.mp4?token=1467913795_5faf17e8319b2988a149bfba6a686f40']
                return item
            except Exception as e:
                format_exc(self, "_extract_more", e)


