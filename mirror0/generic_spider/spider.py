
from ConfigParser import NoOptionError
from exceptions import ValueError
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

    def __init__(self, **kw):
        try:
            scrapy.Spider.__init__(self, **kw)

            self.video_processor = None

            """attributes to be overridden"""
            self._index = NotImplementedError()
            self.disabled_pipelines = []

            self._page_count = 0
            self._dates = []
            self._links = {} 
            self._video_msg = {}
            self._existent = {}
            self._next_page_url_interrupted = ""
            self._retry_count = 0
            self._lnk_pos = 0
            self._total_count = 0
            self._object_cleaner = None

            dispatcher.connect(self._spider_idle, scrapy.signals.spider_idle)

            if kw.get('no_index', False):
                self._index = None
            else:
                self._index = Index(self.BASE_DOMAIN)

            self.__first_page = kw.get('first_page', False)

            self.start_url = kw.get('start_url')

            self._object_cleaner = kw.get('object_cleaner') 

            if "/" == self.start_url[0]:
                self.start_url = self.BASE_URL + self.start_url
            log("\n\nSTART: %s" % self.start_url, INFO)
            self.logidx("\nLog for %s started %s" % (self.start_url, time.strftime("%b %d %H:%M:%S %Y")))

            self._per_url_regex_xpath = () 
            self._debug_url = ""

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
        #if self._debug_url:
        #    return
        assert url in self._links, "Spider.start: bad url"
        if "?" == self._links[url]:
            self._links[url] = ObjectStateIndicators()
        self._links[url].start(state_id)

    def finalize_state(self, url, state_id):
        #if self._debug_url:
        #    return
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
        super(Spider, self).spider_close(spider)
        self._spider_idle(spider)

    def _spider_idle(self, spider):
        """Collect more links, starting from the place previously stopped"""
        try:
            log("Spider {0} idle start".format(self.name), DEBUG)
            if self.video_processor:
                self.video_processor.wait_all_finished(self)
            if self._links or self._existent:
                #should complete all requests before going further
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
                    self.logidx("Requesting {0}".format(self._next_page_url_interrupted))
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
#"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36" 
            },
            meta=meta_,
            dont_filter=dont_filter_,
            errback=errback_,
            )

    def _request_failed(self, failure):
        log("Failed: %s" % str(failure), ERROR)

        """ HttpError ?
        if isinstance(failure.value, spidermiddlewares.HttpError):
            response = failure.value.response
            log("Code ", str(response.status))
        else:
            log("Failed miserably: %s" % str(failure))"""
        log("Failed: %s" % str(failure))

    def _run_item(self, response):
        try:
            url = response.request.url
            if not url in self._links:
                log("Response url doesn't match: %s" % url, INFO)
            item = self._item_class(self)
            item['raw_url'] = url
            response = self._prepare_response(response)
            item['raw_html'] = response.selector
            #item['raw_text'] = response.body
            return item
        except Exception as e:
            format_exc(self, "_run_item", e)

    def _links_from_response_per_url(self, response):
        for tpl in self._per_url_regex_xpath:
            try:
                lregex, lxpath, webdriver = tpl
            except ValueError as e:
                lregex, lxpath = tpl
                webdriver = ""
                
            print lregex, response.url
            if re.search(lregex, response.url):
                links = response.xpath(lxpath).extract()
                return links, webdriver
        return None, None 

    def _collect_next_page_links(self, response):
        try:
            links = ""            
            webdriver = ""
            try:
                self._debug_url = Config.value(mirror0.SECTION_COMMON, "debug_url") 
                if self._debug_url:
                    links = [url for url in str.splitlines(self._debug_url) if url]
                webdriver = "do_use"
            except Exception:
                pass
            if not links:
                links, webdriver = self._links_from_response_per_url(response)
                if not links:
                    links = self._links_from_response(response)
                    webdriver = ""
                if not links:
                    msg = "NO LINKS %s" % response.request.url 
                    log(msg, WARNING)
                    self.logidx(msg, response.body)
                else:
                    log("Raw links: {}".format(len(links)), DEBUG)

            links = [(self.BASE_URL + lnk if "/" == lnk[0] else lnk) for lnk in links]
            try:
                first_n = int(Config.value(mirror0.SECTION_COMMON, "debug_first_n"))
                links[:] = links[:first_n]
                log("ONLY FIRST {}".format(first_n))
            except NoOptionError:
                pass

            next_url = self._extract_next_url(response)
            if next_url:
                log("Next page: %s" % next_url, WARNING)
            else:
                log("FINISHED at %s" % response.request.url, WARNING)
                self.logidx("NO SHOW MORE %s" % response.request.url, response.body)

            try:
                debug_link_regex = Config.value(mirror0.SECTION_COMMON, "debug_link_regex")
                print(debug_link_regex)
                if debug_link_regex:
                    links = [lnk for lnk in links if re.search(debug_link_regex, lnk)]
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
                else:
                    self._links[lnk] = "?"

            self._total_count += len(links)
            log("Links collected total: %i this page: %i to process: %i duplicate within page: %i" % (self._total_count, len(links), len(self._links), duplicate), 
                WARNING)

            if INDEX_ONLY and next_url:
                return Spider._request(url_=next_url, callback_=self._collect_next_page_links)
            else:
                return self._request_next_page_links(next_url, webdriver)
        except Exception as e:
            format_exc(self, "collect_next_page_links", e)

    def _request_next_page_links(self, next_url, webdriver):

        if (len(self._links) >= LINKS_BATCH or not next_url):
            #request articles from collected links
            requests = []
            for url in self._links:
                requests.append(Spider._request(
                    url_=url, 
                    callback_=self._run_item,
                    errback_=self._request_failed,
                    dont_filter_=True,
                    meta_={"webdriver" : webdriver,},))
                self._lnk_pos += 1
            self._next_page_url_interrupted = next_url
            #scrapy sends them in the reverse order
            requests.reverse()
            log(json.dumps(self._links, separators=("\n"," ")), DEBUG)
            log("Requesting articles")
            return requests

        if next_url:
            return Spider._request(url_=next_url, callback_=self._collect_next_page_links)


