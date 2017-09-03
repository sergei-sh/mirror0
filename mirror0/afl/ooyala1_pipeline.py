""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: The extraction of video hosted at ooyala.com 
"""

from logging import ERROR, DEBUG, WARNING
import os.path

import scrapy
from mirror0.generic_spider import MediaPipelineEx
from mirror0.generic_spider import Spider
from mirror0.sscommon.aux import log, format_exc

#defined here to avoid circular inclusion
OOYALA_JS_ID = "O_TYPE2"

class Ooyala1Pipeline(MediaPipelineEx):
    """The finalizing request in ooyala extraction chain
    """
    STATE_ID = "OOY1"

    def __init__(self):
        super(Ooyala1Pipeline, self).__init__(dont_filter=True)
        self._less_vid_count = 0

    def open_spider(self, spider):
        super(Ooyala1Pipeline, self).open_spider(spider)
        self._spider = spider

    def get_media_requests(self, item, info):
        try:
            url = item['raw_url']

            self._less_vid_count += 1
            if self._spider.less_vid and self._less_vid_count % 15:
                return

            if OOYALA_JS_ID in item.started_states():
                log("Ooyala1 skipping %s" % item['raw_url'], DEBUG)
                return
            else:
                if item['ooyala_video_ids']:
                    assert item['ooyala_urls'], "Should either fail in 0 or has urls"
                else:
                    log("Ooyala1 NOVID %s" % item['raw_url'], DEBUG)
                    return

            log("Ooyala1 processing %s" % item['raw_url'], DEBUG)
            item.start(Ooyala1Pipeline.STATE_ID)
            return self.yield_requests(self, item, 'ooyala_urls')
        except Exception as e:
            format_exc(self, "get_media_requests", e)
            item['vlog']("Ooyala1: " + str(e))

    @staticmethod                    
    def yield_requests(inst, item, urls_field):
        try:
            assert item[urls_field], "Should be called for a filled item"
            i = 1
            for vid in item[urls_field]:
                log("Started downloading video %s for %s" % (Ooyala1Pipeline.__vid_name(inst, i), item['raw_url']))
                yield scrapy.Request(
                    url=vid,
                    method="GET",
                    headers={
                        "Accept" : "*/*",
                        "User-Agent" : "Mozilla",
                    },
                    meta={'item':item, 'number':i},
                )
                i += 1
        except Exception as e:
            format_exc(inst, "yield_requests", e)

    def media_downloaded(self, response, request, info):
        try:
            self.handle_downloaded(self, response)
        except Exception as e:
            format_exc(self, "media_downloaded", e)

    @staticmethod
    def __vid_name(inst, num):
       return inst.STATE_ID + "_" + str(num)

    @staticmethod
    def handle_downloaded(inst, response, vid_name = ""):
        try:
            item = response.meta['item']
            url = item['raw_url']
            if not vid_name:
                vid_name = Ooyala1Pipeline.__vid_name(inst, response.meta['number'])
            with open(os.path.join(item['path'], vid_name + ".mp4"), "wb") as vid_f:
                vid_f.write(response.body)
            log("Finished downloading video %s for %s %s (%i)" % (vid_name, item['title'], item['raw_url'], len(response.body)))
            if len(response.body) < 5000:
                item['vlog'](response.body)
            #caller either should have id or finish by itself
            if hasattr(inst, 'STATE_ID'):
                item.finish(inst.STATE_ID)
        except Exception as e:
            format_exc(inst, "handle_downloaded", e)

    def media_failed(self, failure, request, info):
        self.handle_failed(self, failure, request)
    
    @staticmethod
    def handle_failed(inst, failure, request):
        try:
            format_exc(inst, "media_failed", failure)
            item = request.meta['item']
            item['vlog']("Ooyala1: " + str(failure))
        except Exception as e:
            format_exc(inst, "handle_failed", e)




