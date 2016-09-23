
import json
import re

import scrapy

import mirror0.generic_spider 
from mirror0.afl.afl_fs_pipeline import AflFSPipeline
from mirror0.news.module0 import NewsItem
from mirror0.sscommon.aux import format_exc
from mirror0 import Config

CONFIG_SECTION = "NewsComAu"

class NewsSpider(mirror0.generic_spider.Spider):
    custom_settings =  { "ITEM_PIPELINES" : 
            { 
                'mirror0.news.module1.NewsExtractorPipeline' : 543,
                'mirror0.afl.afl_fs_pipeline.AflFSPipeline' : 544,
                'mirror0.generic_spider.text_image_pipeline.TextImagePipeline': 545,
                'mirror0.generic_spider.meta_file_pipeline.MetaFilePipeline': 546,
                'mirror0.news.news_spider.Niux': 547,
                'mirror0.news.module0.Linja': 548,
            }

    }

    name = "news"
    BASE_DOMAIN = "www.news.com.au"
    allowed_domains = [BASE_DOMAIN]
    BASE_URL = "http://" + BASE_DOMAIN

    _index_file_name = "news.log"
    _item_class = NewsItem

    HOME_PAGE = BASE_URL

    @classmethod
    def create_start_urls(cls):
        urls = []#[cls.HOME_PAGE]
        urls += [u for u in str.splitlines(Config.value(CONFIG_SECTION, "start_urls")) if u]
        return urls

    def __init__(self, **kw):
        try:
            mirror0.generic_spider.Spider.__init__(self, **kw)
            self._per_url_regex_xpath = ( 
                (r"video/sport/afl", "//a[@class='vms-list-item module']/@href"), 
                ("sport/afl^", '//div[@class="story-block "]/a[@class="thumb-link"]/@href'), #main page
                ("", '//div[@class="story-block "]/h4[@class="heading"]/a/@href'), #more-stories, clubs 
                )

        except Exception as e:
            format_exc(self, "__init__", e)

    def _links_from_response(self, response):
        try:
            links = []

            return links

        except Exception as e:
            format_exc(self, "_links_from_response", e)
            return None

    def _extract_next_url(self, response):

        match = re.search(r'nextPage[^\}]*({\"vgnextcomponentid.*\"\})', response.body)
        if not match:
            return None
        self._pagination = json.loads(match.group(1))
        next_url = json.dumps(self._pagination, separators=('&','=')).replace('"', '').replace('}', '').replace('{', '')
        next_url = self.BASE_URL + "/render/component?" + next_url
        return next_url             


from logging import ERROR, DEBUG, WARNING

from mirror0.generic_spider import MediaPipelineEx
from mirror0.sscommon.aux import log, format_exc

class Niux(MediaPipelineEx):
    STATE_ID = "NIU"

    def __init__(self):
        super(self.__class__, self).__init__(dont_filter=True)

    def get_media_requests(self, item, info):
        item['playlist_url'] = "" 

        if item['ooyala_id']:
            try:
                item.start(self.STATE_ID)
                url = "http://player.ooyala.com/player_api/v1/metadata/embed_code/89a379a0e1e94feca5bb87c46a8b2d5e/" + item['ooyala_id'] 
                log("Preparing youtube-dl playlist %s " % (item['raw_url']), DEBUG)
                request = scrapy.Request(
                    url=url,
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

    def media_downloaded(self, response, request, info):
        try:
            match = re.search(r'http://newsvidhd[^\|]+(\d{4}/\d{2}/\d{2}/)', response.body)
            try:
                item = response.meta['item']
                item['vlog'](response.body)
                date = match.group(1)
                match = re.search(r"[\w]+", response.body[match.end():])
                vid_name = match.group(0)
                item['playlist_url'] = "http://newsvidhd-vh.akamaihd.net/i/foxsports/prod/archive/"\
                     + date + "," + vid_name + ",.mp4.csmil/master.m3u8"
                item.finish(self.STATE_ID)
                return item
            except Exception as e:
                log("Y-dl playlist extraction failed %s: %s" % (item['raw_url'], str(e)), ERROR)
                item['vlog'](response.body)
                return item
        except Exception as e:
            format_exc(self, "media_downloaded", e)

    def media_failed(self, failure, request, info):
        log("Ooyala0 failed: %s" % str(failure), ERROR)


