""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

import json
import re

import scrapy

import mirror0.generic_spider 
from mirror0.wb.wb_item import WbItem
from mirror0.sscommon.aux import format_exc
from mirror0 import Config

CONFIG_SECTION = "WesternBulldogs"

class WbSpider(mirror0.generic_spider.Spider):
    """Spider implementation/xpaths customized for exact website
    """

    custom_settings =  { "ITEM_PIPELINES" : 
            { 
                'mirror0.wb.wb_extractor_pipeline.WbExtractorPipeline' : 543,
                'mirror0.wb.wb_fs_pipeline.WbFSPipeline' : 544,
                'mirror0.generic_spider.text_image_pipeline.TextImagePipeline': 545,
                'mirror0.generic_spider.meta_file_pipeline.MetaFilePipeline': 546,
                'mirror0.afl.ooyala0_pipeline.Ooyala0Pipeline': 547,
                'mirror0.afl.ooyala1_pipeline.Ooyala1Pipeline': 548,
                'mirror0.afl.ooyala_js_pipeline.OoyalaJSPipeline': 549,
            }

    }

    name = "wb"
    BASE_DOMAIN = "www.westernbulldogs.com.au"
    allowed_domains = [BASE_DOMAIN]
    BASE_URL = "http://" + BASE_DOMAIN

    _index_file_name = "wb.log"
    _item_class = WbItem

    HOME_PAGE = BASE_URL

    @classmethod
    def create_start_urls(cls):
        urls = [cls.HOME_PAGE]
        urls += [u for u in str.splitlines(Config.value(CONFIG_SECTION, "start_urls")) if u]
        return urls

    def __init__(self, **kw):
        try:
            mirror0.generic_spider.Spider.__init__(self, **kw)
            self.less_vid = kw.get('less_vid', False)

        except Exception as e:
            format_exc(self, "__init__", e)

    def _prepare_response(self, response):
        return scrapy.http.HtmlResponse(url=response.url, body=response.body)

    def _links_from_response(self, response):
        response = self._prepare_response(response)
        try:
            if self.HOME_PAGE == response.url:
                match_info = response.xpath("//div[@class='buttons']/a[contains(text(), 'Match Information')]/@href").extract_first()
                if match_info:
                    pos = match_info.find("#")
                    links = [match_info[:pos]]
                    return links
                else:
                    return [] 
        
            links =  response.xpath("//div[re:test(@class, 'list-item')][not(ancestor::*[re:test(@class, 'double-col')])]/div[re:test(@class, 'inner')]/h4/a/@href").extract()
            """if not links:
                links = response.xpath("//div[re:test(@class, 'list-item')]/div[re:test(@class, 'inner')]/h4/a/@href").extract()"""
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

            


