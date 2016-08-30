
import json
from logging import ERROR, INFO, WARNING, DEBUG
import re
import time

import scrapy.http

import mirror0.generic_spider 
from mirror0 import Config
from mirror0.afl.afl_item import AflItem
from mirror0.sscommon.aux import format_exc, log

CONFIG_SECTION = "Afl"

class AflSpider(mirror0.generic_spider.Spider):
    custom_settings =  { "ITEM_PIPELINES" : 
            {'mirror0.afl.afl_extractor_pipeline.AflExtractorPipeline' : 543,
             'mirror0.afl.afl_fs_pipeline.AflFSPipeline' : 544,
             'mirror0.generic_spider.text_image_pipeline.TextImagePipeline': 545,
             'mirror0.generic_spider.meta_file_pipeline.MetaFilePipeline': 546,
             'mirror0.afl.ooyala0_pipeline.Ooyala0Pipeline': 547,
             'mirror0.afl.ooyala1_pipeline.Ooyala1Pipeline': 548,
             'mirror0.afl.ooyala_js_pipeline.OoyalaJSPipeline': 549,
             'mirror0.afl.twitter_pipeline.TwitterPipeline0': 550,
             'mirror0.afl.twitter_pipeline.TwitterPipeline1': 551,
             'mirror0.afl.twitter_pipeline.TwitterPipeline2': 552,
            }
    }

    BASE_DOMAIN = "www.afl.com.au"
    BASE_URL = "http://" + BASE_DOMAIN
    name = "afl"
    allowed_domains = [BASE_DOMAIN]

    _index_file_name = "afl.log"
    _item_class = AflItem

    @classmethod
    def create_start_urls(cls):
        return [u for u in str.splitlines(Config.value(mirror0.afl.afl_spider.CONFIG_SECTION, "start_urls")) if u]   

    def _prepare_response(self, response):
        return scrapy.http.HtmlResponse(url=response.url, body=response.body)

    def __init__(self, **kw):
        try:
            mirror0.generic_spider.Spider.__init__(self, **kw)

           
            self.less_vid = kw.get('less_vid', False)
          #in this spider videos are downloaded with the framework so no need to wait for additional processes  
            self.video_processor = self

            self._per_url_regex_xpath = (
                ("nabchallenge" , "//h4[@class='partial--finals-video__caption']/a/@href | //h3[re:test(text(), 'News')]/parent::div/parent::div/following::div/div/div[re:test(@class, 'list-item')]/div[re:test(@class, 'inner')]/h4/a/@href"),
            )


        except Exception as e:
            format_exc(self, "__init__", e)

    def wait_all_finished(self, spider):
        pass

    def _links_from_response_per_url(self, response):
        response = self._prepare_response(response)
        return super(AflSpider, self)._links_from_response_per_url(response)

    def _links_from_response(self, response):
        response = self._prepare_response(response)
        try:
            links =  response.xpath("//div[re:test(@class, 'list-item')][not(ancestor::*[re:test(@class, 'double-col')])]/div[re:test(@class, 'inner')]/h4/a/@href").extract()
            if not links:
                links = response.xpath("//div[re:test(@class, 'list-item')]/div[re:test(@class, 'inner')]/h4/a/@href").extract()
            return links

        except Exception as e:
            format_exc(self, "_links_from_response", e)
            return None

    def _extract_next_url(self, response):
        response = self._prepare_response(response)
        #other pages OR first page
        match = re.search(r'nextPage[^\}]*({\"vgnextcomponentid.*\"\})', response.body)
        if not match:
            return None
        self._pagination = json.loads(match.group(1))
        next_url = json.dumps(self._pagination, separators=('&','=')).replace('"', '').replace('}', '').replace('{', '')
        next_url = self.BASE_URL + "/render/component?" + next_url
        return next_url             



