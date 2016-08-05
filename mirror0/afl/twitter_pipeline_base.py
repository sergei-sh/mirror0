
from logging import ERROR, DEBUG, WARNING, INFO
import scrapy

from mirror0.generic_spider import MediaPipelineNoFilter
from mirror0.sscommon.aux import log, format_exc

class TwitterPipelineBase(MediaPipelineNoFilter):
    """Get either a list or a single link string"""
    def extract_next_link(self, response_text, item):
        raise NotImplementedError()

    def start_state_if_needed(self, item, data_num):
        pass

    def get_media_requests(self, item, info):
        item_url = item['raw_url']
        try:
            data_cnt = len(item['twitter_data'])
            if data_cnt:
                log("%s extracting for %s" % (self.__class__.__name__, item['raw_url']), DEBUG)
            for data_num in range(0, data_cnt):
                prev_response = item['twitter_data'][data_num]
                item['twitter_data'][data_num] = None 
                if not prev_response:
                    log("Stopped num %i for %s" % (data_num, item_url), INFO)
                else:
                    err_msg = ""
                    try:
                        next_link = self.extract_next_link(prev_response)
                    except Exception as e:
                        err_msg = str(e) 
                        next_link = None
                    if next_link:
                        self.start_state_if_needed(item, data_num)
                        log("%i requesting %s for %s" % (data_num, next_link, item_url), DEBUG)
                        yield scrapy.Request(
                            url=next_link,
                            method="GET",
                            headers={
                                "Accept" : "*/*",
                                "User-Agent" : "Mozilla",
                            },
                            meta={'item':item, 'data_num':data_num},
                        )
                    else:
                        item['vlog'](("data_num %i\n" % data_num) + prev_response.body)
                        log("Extraction failed num %i: %s for %s" % (data_num, err_msg, item_url), DEBUG)

        except Exception as e:
            format_exc(self, "get_media_requests %s" % item_url, e)

    def media_downloaded(self, response, request, info):
        item = response.meta['item']
        try:
            data_num = response.meta['data_num']
            item['twitter_data'][data_num] = response
        except Exception as e:
            format_exc(self, "media_downloaded %s" % item['raw_url'], e)

    def media_failed(self, failure, request, info):
        item = request.meta['item']
        try:
            log("%s failed: %s" % (self.__class__.__name__, str(failure)), ERROR)
        except Exception as e:
            format_exc(self, "media_failed %s" % item['raw_url'], e)



