
import mirror0.generic_spider 
from mirror0.yahoo.yahoo_item import YahooItem
from mirror0.sscommon.aux import format_exc
from mirror0 import Config
"""
    V_OK, V_FAIL, V_NOVID, V_UNKNOWN = range(4)

    def finalize_video(self, url, result, message = ""):
        assert url in self._links, "Spider: bad video url %s \n %s" % (url, json.dumps(self._links, separators=("\n", "=")))
        if Spider.V_OK == result:
            self._links[url] += ",VOK"
        elif Spider.V_FAIL == result:
            self._links[url] += ",VIDEOF"
        elif Spider.V_NOVID == result:
            self._links[url] += ",NOVID"
        elif Spider.V_UNKNOWN == result:
            self._links[url] += ",VUNKNOWN"
        else:
            assert False, "Spider: bad video result"
        if message:
            self._video_msg[url] = message

if "OK,VOK" == result or "OK,NOVID" == result:
"""


CONFIG_SECTION = "Yahoo"

class YahooSpider(mirror0.generic_spider.Spider):
    custom_settings =  { "ITEM_PIPELINES" : 
            {'mirror0.yahoo.yahoo_extractor_pipeline.YahooExtractorPipeline': 544,
            'mirror0.yahoo.yahoo_fs_pipeline.YahooFSPipeline': 545,
            'mirror0.yahoo.stream_pipeline.StreamPipeline': 546,
            'mirror0.generic_spider.text_image_pipeline.TextImagePipeline': 547,
            'mirror0.generic_spider.meta_file_pipeline.MetaFilePipeline': 548, }
    }

    name = "yahoo"
    BASE_DOMAIN = "au.sports.yahoo.com"
    allowed_domains = [BASE_DOMAIN]
    BASE_URL = "https://" + BASE_DOMAIN

    _index_file_name = "yahoo.log"
    _item_class = YahooItem

    @classmethod
    def create_start_urls(cls):
        _lines = str.splitlines(Config.value(CONFIG_SECTION, "start_urls"))
        urls = [l for l in _lines if l]
        assert 1 == len(urls)
        return urls

    def __init__(self, **kw):
        try:
            mirror0.generic_spider.Spider.__init__(self, **kw)
            #super(self.__class__, self).__init__(kw)

            self._per_url_regex_xpath = {}

        except Exception as e:
            format_exc(self, "__init__", e)

    def _links_from_response(self, response):
        try:
            links = response.xpath(\
            "//article[@class='masonry-asset']/div[@class='masonry-content']/h3[@class='masonry-title']/a/@href | //a[@class='hero-caption-title-link']/@href"\
            ).extract()
            return ["https:" + lnk for lnk in links]

        except Exception:
            return None

    def _extract_next_url(self, response):
        #other pages OR first page
        return self.BASE_URL + \
               (response.xpath("//a[@class='load-location']/@data-next-url").extract_first() or \
                response.xpath("//div/div[re:test(@class, 'pagination')]/a/@data-url").extract_first())
             


