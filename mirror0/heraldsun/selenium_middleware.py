""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: The middleware loading pages with the Selenium and sending back the 
fully processed page
"""

import logging

from selenium.common.exceptions import TimeoutException
from scrapy.http import HtmlResponse

from mirror0.sscommon.aux import log

class SeleniumMiddleware(object):
    """Uses Selenium for the items having the key in their meta set"""
    def process_request(self, request, spider):
        if ("webdriver" in request.meta and request.meta["webdriver"] == "do_use"):
            log("Selenium requesting {}".format(request.url))
            try:
                spider.driver.get(request.url)
            except TimeoutException as we:
                log("Web driver: timeout at {}".format(request.url), logging.ERROR)

            return HtmlResponse(spider.driver.current_url, body=spider.driver.page_source, encoding="utf-8", request=request)
