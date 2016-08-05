
import logging
from logging import DEBUG, INFO, WARNING, ERROR
import os
import re
from scrapy.exceptions import DropItem
import time

import json

import scrapy
from scrapy import spidermiddlewares
from scrapy.xlib.pydispatch import dispatcher

import mirror0
from mirror0 import Config
from mirror0 import Index
from mirror0.sscommon.aux import format_exc, log

from .text_image_pipeline import TextImagePipeline
from .object_state_indicators import ObjectStateIndicators

INDEX_ONLY = False
LINKS_BATCH = 1 

class Spider(scrapy.Spider):
    _index_file_name = NotImplementedError()
    name = NotImplementedError()
    _item_class = NotImplementedError()

    @classmethod
    def create_start_urls():
        raise NotImplementedError()

    def _links_from_response(self, response):
        raise NotImplementedError()

    def _extract_next_url(self, response):
        raise NotImplementedError()

    def _prepare_response(self, response):
        return response

    def _is_successful(self, states):
        return TextImagePipeline.STATE_ID in states.finished and not states.incomplete

    @classmethod 
    def init_idx_log(cls):
        Spider._idx_file = os.path.join(Config.value(mirror0.SECTION_COMMON, "log_directory"), cls._index_file_name)
        with open(Spider._idx_file, "w") as f:
            f.write("Log for %s initially started %s\n" % (cls.name, time.strftime("%b %d %H:%M:%S %Y")))

    def logidx(self, msg, html=None):
        with open(self._idx_file, "a") as f:
            f.write(msg + "\n")
        """logging.getLogger("linkwise").info(msg)
        if html:
            logging.getLogger("html").info("\n" + msg + "\n" + html)"""

    def __init__(self, **kw):
        try:
            scrapy.Spider.__init__(self, **kw)

            self.video_processor = None

            self._index = NotImplementedError()
            self._per_url_regex_xpath = NotImplementedError()

            self._page_count = 0
            self._dates = []
            self._links = {} 
            self._video_msg = {}
            self._existent = {}
            self._next_page_url_interrupted = ""
            self._retry_count = 0
            self._lnk_pos = 0
            self._total_count = 0

            dispatcher.connect(self._spider_idle, scrapy.signals.spider_idle)

            if kw.get('no_index', False):
                self._index = None
            else:
                self._index = Index(self.BASE_DOMAIN)

            self.__first_page = kw.get('first_page', False)

            self.start_url = kw.get('start_url')

            if "/" == self.start_url[0]:
                self.start_url = self.BASE_URL + self.start_url
            log("\n\nSTART: %s" % self.start_url, INFO)
            self.logidx("\nLog for %s started %s" % (self.start_url, time.strftime("%b %d %H:%M:%S %Y")))

            self._per_url_regex_xpath = {}

        except Exception as e:
            format_exc(self, "__init__", e)

    def start_requests(self):
        try:
            yield self._request(
                url_=self.start_url,
                callback_=self._collect_next_page_links,
                )
        except Exception as e:
            format_exc(self, "start_requests", e)


    def start_state(self, url, state_id):
        assert url in self._links, "Spider.start: bad url"
        if "?" == self._links[url]:
            self._links[url] = ObjectStateIndicators()
        self._links[url].start(state_id)

    def finalize_state(self, url, state_id):
        assert url in self._links, "Spider.finalize: bad url"
        self._links[url].finish(state_id)
            
    def started_states(self, url):
        return self._links[url].started

    def _index_successful(self):
        try:
            self._links.update(self._existent)
            self._existent.clear()
            for link, state in self._links.viewitems():
                if not type(state) is str and self._is_successful(state):
                     if self._index:
                        self._index.add(link)
            if self._index:
                self._index.save()
        except Exception as e:
            format_exc(self, "_index_successful", e)

    def spider_close(self, spider):
        super(AflSpider, self).spider_close(spider)
        self._spider_idle(spider)

    def _spider_idle(self, spider):

        """Collect more links, starting from the place previously stopped"""
        try:
            if self._links or self._existent:
                #should complete all requests before going further
                if self.video_processor:
                    self.video_processor.wait_all_finished(self)
                self._index_successful()
                for link, states in self._links.viewitems():
                    self.logidx("%s %s" % (str(states), link))

                lost = sum(1 for lnk, result in self._links.viewitems() if "?" == result)
                ok = sum(1 for lnk, result in self._links.viewitems() if not type(result) is str and self._is_successful(result))
                log("Lost links: %i, OK: %i" % (lost, ok), WARNING)
                self._links.clear()

                if self.__first_page:
                    return

                if self._next_page_url_interrupted:
                    log("Idle, start collecting links")
                    req = Spider._request(self._next_page_url_interrupted, self._collect_next_page_links)
                    self._next_page_url_interrupted = ""
                    self.crawler.engine.crawl(req, spider)
        except Exception as e:
            format_exc(self, "_spider_idle", e)

    @staticmethod
    def _request(url_, callback_, errback_ = None, dont_filter_=True, meta_=None):
        return scrapy.Request(
            url=url_,
            callback=callback_,
            method="GET",
            headers={
                "Accept" : "*/*",
                "User-Agent" : "Mozilla",
            },
            meta=meta_,
            dont_filter=dont_filter_,
            errback=errback_,
            )

    def _request_failed(self, failure):
        log("Failed: %s" % str(failure), ERROR)

        if isinstance(failure.value, spidermiddlewares.HttpError):
            response = failure.value.response
            log("Code ", str(response.status))
        else:
            log("Failed miserably: %s" % str(failure))

    def _run_item(self, response):
        try:
            url = response.request.url
            if not url in self._links:
                log("Discarding: %s" % url, WARNING)
                return
            item = self._item_class(self)
            item['raw_url'] = url
            response = self._prepare_response(response)
            item['raw_html'] = response.selector
            #item['raw_text'] = response.body
            return item
        except Exception as e:
            format_exc(self, "_run_item", e)

    def _links_from_response_per_url(self, response):
        for lregex, lxpath in self._per_url_regex_xpath.viewitems():
            if re.search(lregex, response.url):
                links = response.xpath(lxpath).extract()
                return links

    def _collect_next_page_links(self, response):
        try:
            links = self._links_from_response_per_url(response)
            if not links:
                links = self._links_from_response(response)
            if not links:
                msg = "NO LINKS %s" % response.request.url 
                log(msg, WARNING)
                self.logidx(msg, response.body)

            links = [(self.BASE_URL + lnk if "/" == lnk[0] else lnk) for lnk in links]
            """DEBUG"""
            links[:] = links[:5]
            """END"""            

            next_url = self._extract_next_url(response)
            if next_url:
                log("Next page: %s" % next_url, WARNING)
            else:
                log("FINISHED at %s" % response.request.url, WARNING)
                self.logidx("NO SHOW MORE %s" % response.request.url, response.body)

            try:
                debug_link = Config.value(mirror0.SECTION_COMMON, "debug_link")
                print(debug_link)
                if debug_link:
                    links = [lnk for lnk in links if re.search(debug_link, lnk)]
            except Exception:
                pass

            #links duplicated within page
            duplicate = 0
            #being stored in index 
            for lnk in links:
                if lnk in self._links:
                    duplicate += 1
                elif self._index and self._index.has(lnk):
                    log("Article link is in index, skipping: %s" % lnk, INFO)
                    self._existent[lnk] = "EXISTS"
                else:
