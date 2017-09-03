""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

import mirror0.generic_spider 
from mirror0.watoday.watoday_item import WatodayItem
from mirror0.sscommon.aux import format_exc, url_path
from mirror0 import Config

import re

CONFIG_SECTION = "Watoday"

class WatodaySpider(mirror0.generic_spider.Spider):
    """Spider implementation/xpaths customized for exact website
    """

    custom_settings =  { "ITEM_PIPELINES" : 
            {'mirror0.watoday.watoday_extractor_pipeline.WatodayExtractorPipeline': 544,
            'mirror0.watoday.watoday_fs_pipeline.WatodayFSPipeline': 545,
            'mirror0.yahoo.stream_pipeline.StreamPipeline': 546,
            'mirror0.generic_spider.text_image_pipeline.TextImagePipeline': 547,
            'mirror0.generic_spider.meta_file_pipeline.MetaFilePipeline': 548, 
            'mirror0.afl.TwitterPipeline0': 549, 
            'mirror0.afl.TwitterPipeline1': 550, 
            'mirror0.afl.TwitterPipeline2': 551, 
            }
    }

    name = "watoday"
    BASE_DOMAIN = "www.watoday.com.au"
    allowed_domains = [BASE_DOMAIN]
    BASE_URL = "http://" + BASE_DOMAIN

    _index_file_name = "watoday.log"
    _item_class = WatodayItem

    @classmethod
    def create_start_urls(cls):
        _lines = str.splitlines(Config.value(CONFIG_SECTION, "start_urls"))
        urls = [l for l in _lines if l]
        return urls

    def __init__(self, **kw):
        try:
            mirror0.generic_spider.Spider.__init__(self, **kw)

        except Exception as e:
            format_exc(self, "__init__", e)

    TITLE_PAGE = BASE_DOMAIN + "/afl"
    VIDEO_PATH = "/video"

    def _links_from_response(self, response):
        try:
            if self.start_url.endswith(self.TITLE_PAGE):
                links = response.xpath("//article[re:test(@class, 'story')]/descendant::h3[@class='story__headline']/a/@href")\
                .extract()
                links = [lnk for lnk in links if self.TITLE_PAGE in lnk or self.VIDEO_PATH in lnk]
            else:
                links = response.xpath(\
                "//article[@class='story has-wof']/div[@class='story__wof']/h3[@class='story__headline']/a/@href | //article[re:test(@class, 'has-wof')]/h3[@class='story__headline']/a/@href"
                ).extract()
            return links

        except Exception as e:
            format_exc(self, "_links_from_response", e)
            return None

    def _run_item(self, response):
        try:
            item = super(WatodaySpider, self)._run_item(response)

            if self.start_url.endswith(self.TITLE_PAGE):
                upath = url_path(response.request.url)
                if upath.startswith("video"):
                    item['out_dir'] = "video"
                else:
                    item['out_dir'] = "title-page"

            return item
        except Exception as e:
            format_exc(self, "_run_item", e)

    def _extract_next_url(self, response):
        if "injury-news" in response.url:
            match = re.search(r"injury-news\?p=(\d)", response.url)
            if match:
                page = int(match.group(1))
                page += 1
                LAST_INJURY_PAGE = 6
                if LAST_INJURY_PAGE == page:
                    return None
            else:
                SECOND_INJURY_PAGE = 2
                page = SECOND_INJURY_PAGE 
            return self.BASE_URL + "/afl/injury-news?p={0}".format(page)
        else:
            return None
             


