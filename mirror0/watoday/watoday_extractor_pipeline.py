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

class WatodayExtractorPipeline(RawExtractorPipeline):
    """XPaths/custom logic for item extraction specific to this website.
       Prepares twitter urls.
    """

    def __init__(self):
        RawExtractorPipeline.__init__(self)

        self._title_x = "//article/header/h1[@itemprop='name headline']/text()"
        self._text_paragraph_x = "//article/div[@class='article__body']/p/text() | //div[@id='content-livepost']/div[@class='livepost-wrapper']/descendant::p/text() | //div[@id='content-livepost']/div[@class='livepost-wrapper']/descendant::time/text()"
        self._abstract_paragraph_x = ""
        self._picture_x = "//article/div[@class='article__body']/figure/img/@src | //article/header/figure/img/@src"
        #livepost pictures
        self._picture_x += " | //article/div[@id='content-livepost']/div/div/figure/img/@src"
        #self._time_x = "//div[@class='signature']/div[@class='signature__info']/time/text()"
        #self._time_format_in = ["%B %d %Y - %I:%M%p",]
        self._time_x = "//meta[@property='article:published_time']/@content"
        self._time_format_in = []
        self._time_format_out = "%B %d, %Y, %I:%M %p" 

    def _extract_more(self, item, spider):
            try:
                selector = item['raw_html']
                if "/video" in item['raw_url'] or selector.xpath("//article/descendant::div[re:test(@class, 'inline-player')]"):
                    item['skip_video'] = False
                    log("Video elements found in article %s" % item['raw_url'], DEBUG)
                else:
                    item['skip_video'] = True
                    log("No video elements in article %s" % item['raw_url'], DEBUG)

                item['twitter_data'] = \
                    [re.search(r'status/(\d+)', twit_lnk).group(1) 
                        for twit_lnk in selector.xpath("//blockquote[re:test(@class,'twitter-tweet')]/a[re:test(@href, 'status/(\d+)')]/@href").extract()]
                
                return item
            except Exception as e:
                format_exc(self, "_extract_more", e)


