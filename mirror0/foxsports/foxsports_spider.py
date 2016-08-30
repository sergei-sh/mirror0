
import mirror0.generic_spider 
from mirror0.generic_spider import RawExtractorPipeline
from mirror0.foxsports.foxsports_item import FoxsportsItem
from mirror0.sscommon.aux import format_exc, url_path
from mirror0 import Config

import scrapy

import re

CONFIG_SECTION = "Foxsports"

class FoxsportsSpider(mirror0.generic_spider.Spider):
    custom_settings =  { 
        "ITEM_PIPELINES" : 
            {'mirror0.foxsports.foxsports_extractor_pipeline.FoxsportsExtractorPipeline': 544,
            'mirror0.foxsports.foxsports_fs_pipeline.FoxsportsFSPipeline': 545,
            'mirror0.generic_spider.text_image_pipeline.TextImagePipeline': 547,
            'mirror0.generic_spider.meta_file_pipeline.MetaFilePipeline': 548, 
            'mirror0.foxsports.video_direct_pipeline.VideoDirectPipeline': 549,
            },
       "DOWNLOAD_TIMEOUT" : 900,     
       "CONCURRENT_REQUESTS_PER_DOMAIN" : 1,
       "RETRY_TIMES": 1,
    }

    name = "foxsports"
    BASE_DOMAIN = "www.foxsports.com.au"
    allowed_domains = [BASE_DOMAIN]
    BASE_URL = "http://" + BASE_DOMAIN

    _index_file_name = "foxsports.log"
    _item_class = FoxsportsItem
    NORMAL, VIDEO = range(2)

    @classmethod
    def create_start_urls(cls):
        _lines = str.splitlines(Config.value(CONFIG_SECTION, "start_urls"))
        urls = [l for l in _lines if l]
        return urls

    TITLE_PAGE = BASE_URL + "/afl"
    VIDEO_PATH = BASE_URL + "/video"

    def __init__(self, **kw):
        try:
            mirror0.generic_spider.Spider.__init__(self, **kw)

            if self.start_url.startswith(self.VIDEO_PATH):
                self.mode = self.VIDEO
                self.disabled_pipelines = [mirror0.generic_spider.text_image_pipeline.TextImagePipeline.NAME,
                                           mirror0.generic_spider.raw_extractor_pipeline.RawExtractorPipeline.NAME,]
            else:
                self.mode = self.NORMAL

        except Exception as e:
            format_exc(self, "__init__", e)

    def _is_successful(self, states):
        return not states.incomplete

    def start_requests(self):
        try:
            """if scraping from videos page, getting video links directly from the start page top section"""
            yield self._request(
                url_=self.start_url,
                callback_=(self._collect_next_page_links if self.NORMAL == self.mode else self._run_item),
                )
        except Exception as e:
            format_exc(self, "start_requests", e)

    def _prepare_response(self, response):
        return scrapy.http.HtmlResponse(url=response.url, body=response.body)

    def _links_from_response(self, response):
        try:
            if self.TITLE_PAGE == self.start_url:
                xpath_s = "//section[@class='breaking-news']/header/h1[re:test(text(), 'fantasy')]/../../div/ol/li/article/header/div/h1[@itemprop='name headline']/a/@href | //section[@class='breaking-news']/header/h1[re:test(text(), 'women')]/../../div/ol/li/article/header/div/h1[@itemprop='name headline']/a/@href | //section/header/h1/a[text()='More AFL News']/../../../div/div/div/div/div/article/header/div/h1[@itemprop='name headline']/a/@href"
            else:
                xpath_s = "//article/header[re:test(@class, 'article')]/div/h1/a/@href"
                
            links = response.xpath(xpath_s).extract()
            return links

        except Exception as e:
            format_exc(self, "_links_from_response", e)
            return None

    def _run_item(self, response):
        try:
            if self.mode == self.NORMAL:
                item = super(FoxsportsSpider, self)._run_item(response)
                if self.TITLE_PAGE == self.start_url:
                    item['out_dir'] = "title_page"
                yield item
            elif self.mode == self.VIDEO:
                response = self._prepare_response(response)
                for sel_item in response.selector.xpath("//li[re:test(@class,'fiso-video-mosaic')]"):
                    url = sel_item.xpath("./descendant::meta[@itemprop='contentURL']/@content").extract_first()
                    if url:
                        debug_link_regex = ""
                        try:
                            debug_link_regex = Config.value(mirror0.SECTION_COMMON, "debug_link_regex")
                        except Exception:
                            pass

                        if debug_link_regex:
                            if not re.search(debug_link_regex, url):
                                 continue
                        title = sel_item.xpath("./descendant::meta[@itemprop='headline name']/@content").extract_first()
                        time = sel_item.xpath("./descendant::meta[@itemprop='uploadDate']/@content").extract_first()
                        item = self._item_class(self)
                        item['video_urls'] = [url]
                        item['title'] = RawExtractorPipeline.encode_strip(title)
                        item['raw_url'] = url
                        item['time'] = time 
                        self._links[url] = "?"

                        #"""DEBUG"""
                        yield item
                else:
                    assert "Wrong mode value"

        except Exception as e:
            format_exc(self, "_run_item", e)

    def _extract_next_url(self, response):
        return None
             


