""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: Downloads videos from known locations
"""

from logging import ERROR, DEBUG, WARNING

import os.path
import scrapy
from mirror0.generic_spider import MediaPipelineEx
from mirror0.sscommon.aux import log, format_exc

NO_VIDEO = False

class RequestEx(scrapy.Request):
    def _set_url(self, url):
        super(RequestEx, self)._set_url(url)
        print self._url

class VideoDirectPipeline(MediaPipelineEx):
    """Sends requests for video download from item URL list
    """
    STATE_ID = "VID"

    def __init__(self, **kw):
        kw['dont_filter'] = True
        super(self.__class__, self).__init__(**kw)

    def open_spider(self, spider):
        super(self.__class__, self).open_spider(spider)
        self._spider = spider

    def get_media_requests(self, item, info):

        if NO_VIDEO:
            return

        try:
            for video_url in item['video_urls']:
                self._spider.start_state(item['raw_url'], self.STATE_ID)
                log("VideoDirect downloading %s " % (video_url), DEBUG)
                request = scrapy.Request(
                    url=video_url,
                    #"http://aaa[1]b(2).ru",
                    method="GET",
                    headers={
                        "Accept" : "*/*",
                        "User-Agent" : "Mozilla",
                    },
                    meta={ "item":item, "video_url":video_url}, #"download_timeout":600,
                    dont_filter=True,
                )
                yield request
        except Exception as e:
            format_exc(self, "get_media_requests", e)

    #def _request_done(self, info):
    #    log("RD %s %s" % (info['raw_url'], info['ooyala_video_ids'][0]), WARNING)

    def media_downloaded(self, response, request, info):
        try:
            item = response.meta['item']
            (vpath, vname) = os.path.split(response.meta['video_url'])
            with open(os.path.join(item['path'], vname), "wb") as f: 
                f.write(response.body)

            self._spider.finalize_state(item['raw_url'], self.STATE_ID)
            log("VideoDirect download complete %s for %s" % (request.url, item['raw_url']), WARNING)
        except Exception as e:
            format_exc(self, "media_downloaded", e)

    def media_failed(self, failure, request, info):
        try:
            item = request.meta['item']
            log("VideoDirect download failed %s for %s: %s" % (request.url, item['raw_url'], str(info)), ERROR)

            """DEBUG"""
            video_url = request.meta['video_url']
            (vpath, vname) = os.path.split(video_url)
            vname = "FAIL" + vname
            with open(os.path.join(item['path'], vname), "wb") as f: 
                f.write(video_url)

        except Exception as e:
            format_exc(self, "media_downloaded", e)




