""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: The extraction of video hosted at ooyala.com 
"""

from logging import ERROR, DEBUG, WARNING
import re

import scrapy
from mirror0.generic_spider import MediaPipelineEx
from mirror0.generic_spider import Spider
from mirror0 import SECTION_COMMON
from mirror0.sscommon.aux import log, format_exc
from .ooyala1_pipeline import OOYALA_JS_ID 

NO_VIDEO = False

class Ooyala0Pipeline(MediaPipelineEx):
    """The initial request in the chain needed for ooyala extraction
    """

    def __init__(self):
        super(self.__class__, self).__init__(dont_filter=True)

    def open_spider(self, spider):
        super(self.__class__, self).open_spider(spider)
        self._spider = spider

    def get_media_requests(self, item, info):
        item['ooyala_urls'] = []

        if NO_VIDEO:
            return

        try:
            for id in item['ooyala_video_ids']:
                url = "http://player.ooyala.com/player_api/v1/metadata/embed_code/89a379a0e1e94feca5bb87c46a8b2d5e/" + id
                log("Ooyala 0 requesting %s " % (item['raw_url']), DEBUG)
                request = scrapy.Request(
                    url=url,
                    #callback=self._request_done,
                    method="GET",
                    headers={
                        "Accept" : "*/*",
                        "User-Agent" : "Mozilla",
                    },
                    meta={"item":item},
                    dont_filter=True,
                )
                yield request
        except Exception as e:
            format_exc(self, "get_media_requests", e)

    def _request_done(self, info):
        log("RD %s %s" % (info['raw_url'], info['ooyala_video_ids'][0]), WARNING)

    def media_downloaded(self, response, request, info):
        try:
            match = re.search(r"x200[^\w]+(http[^\"\,]+\.mp4)", response.body)
            item = response.meta['item']
            if match:
                item['ooyala_urls'].append(match.group(1))
                return item
            else:
                item.start(OOYALA_JS_ID )
                log("Ooyala0: type 2 %s" % item['raw_url'], WARNING)
                item['vlog'](response.body)
                return item
                #log("No ooyala match %s %s" % (request.url, item['raw_url']))
        except Exception as e:
            format_exc(self, "media_downloaded", e)

    def media_failed(self, failure, request, info):
        log("Ooyala0 failed: %s" % str(failure), ERROR)





