
import json
from logging import ERROR, DEBUG, WARNING, INFO

from mirror0.sscommon.aux import log, format_exc
from .twitter_pipeline_base import TwitterPipelineBase
from .ooyala1_pipeline import Ooyala1Pipeline

class TwitterPipeline0(TwitterPipelineBase):
    def start_state_if_needed(self, item, data_num):
        pass

    def extract_next_link(self, response_text):
        return "https://twitter.com/i/videos/tweet/" + response_text

class TwitterPipeline1(TwitterPipelineBase):
    STATE_ID = "TW%i"

    def start_state_if_needed(self, item, data_num):
        state_id = TwitterPipeline1.STATE_ID % data_num
        log("Twitter %s started %s" % (state_id, item['raw_url']), INFO)
        item.start(state_id)
   
    def extract_next_link(self, response):
        config_s = response.xpath("//div[@class='player-container']/@data-config").extract_first()
        if config_s:
            config_s = config_s.encode("ascii", "ignore") 
            config = json.loads(config_s)
            return config['vmap_url']

class TwitterPipeline2(TwitterPipelineBase):
    
    def extract_next_link(self, response):
        mp4_lnk = response.xpath("//MediaFile/text()").extract_first()
        if mp4_lnk:
            mp4_lnk = mp4_lnk.strip() 
            log("Downloading %i twitter %s" % (response.meta['data_num'], response.meta['item']['raw_url']))
            return mp4_lnk 

    def media_downloaded(self, response, request, info):
        try:
            data_num = response.meta['data_num']
            state_id = TwitterPipeline1.STATE_ID % data_num
            Ooyala1Pipeline.handle_downloaded(self, response, state_id) 
            response.meta['item'].finish(state_id)
        except Exception as e:
            format_exc(self, "media_downloaded", e)



