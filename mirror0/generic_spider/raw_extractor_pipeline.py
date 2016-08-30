
from datetime import datetime
from logging import ERROR, INFO, WARNING, DEBUG
from pytz import timezone
import string

from scrapy.exceptions import DropItem

from mirror0 import *
from mirror0.sscommon.aux import log, format_exc
from mirror0 import Config

from . import time_utils 

class RawExtractorPipeline(object):
    NAME = "RawExtractorPipeline"

    def __init__(self):
        self._title_x = NotImplementedError()
        self._text_paragraph_x = NotImplementedError()
        self._abstract_paragraph_x = NotImplementedError()
        self._picture_x = NotImplementedError()
        self._time_x = NotImplementedError()
        self._time_format_in = NotImplementedError() 
        self._time_format_out = NotImplementedError() 

    """Additional extractor method"""
    def _extract_more(self, item, spider):
        return item

    @staticmethod
    def encode_strip(uni):
        return uni.encode("ascii", "ignore").replace("/", "").replace("'", "").replace('"', "").replace("`", "").strip()

    def process_item(self, item, spider):
        try:
            if self.NAME in spider.disabled_pipelines:
                return item 

            selector = item['raw_html']
            url = item['raw_url']
            if not url or not selector:
                msg = "Invalid item %s" % str(item)
                log(msg, ERROR)
            #abstr = response.xpath("//p[@class='article-abstract']/text()").extract_first()
            item['title'] = selector.xpath(self._title_x).extract_first()
            if not item['title']:
                item['title'] = selector.xpath("//head/title/text()").extract_first()
            if not item['title']:
                log("No title %s" % url, ERROR)
                raise DropItem()
            item['title'] = item['title'].strip()
            log("RawExtractor got title %s" % item['title'], DEBUG)

            item['title'] = self.encode_strip(item['title'])
            body = ""
            for p in selector.xpath(self._text_paragraph_x).extract():
                body += " " + p
            if body:
                body = body.strip()
            elif self._abstract_paragraph_x:
                body = selector.xpath(self._abstract_paragraph_x).extract_first()
            if not body:
                log("No article text %s" % url, DEBUG)
                body = ""
            item['text'] = body.encode("ascii", "replace").strip(" -\n")
            
            item['pictures'] = selector.xpath(self._picture_x).extract()

            try:
                if self._time_format_in:
                    dt_obj_localized = extract_dt_obj(selector, self._time_x, self._time_format_in)
                else:
                    """Assuming ISO time with timezone on empty format list"""
                    iso_s = selector.xpath(self._time_x).extract_first()
                    dt_obj_localized = time_utils.dt_obj_from_iso(iso_s)
                item['time'] = time_utils.format_utc_from_localized(dt_obj_localized, self._time_format_out) 
            except Exception as e:
                log("No time for %s %s" % (url, str(e)), DEBUG)
                item['time'] = ""

            return self._extract_more(item, spider)
            
        except Exception as e:
            if type(e) == DropItem:
                raise
            format_exc(self, "process_item", e)


def extract_dt_obj(selector, time_xpath, in_format_list):
    time_str = selector.xpath(time_xpath).extract_first()
    time_str = time_str.encode("ascii", "ignore").strip()
    datetime_obj = None
    for fmt in in_format_list:
        try:
            datetime_obj = datetime.strptime(time_str, fmt)
            break
        except:
            pass
    return timezone("Australia/Perth").localize(datetime_obj)

