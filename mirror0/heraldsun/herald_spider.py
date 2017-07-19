
from logging import ERROR, DEBUG, INFO, getLogger
import json
import re
import time
"""
from selenium.webdriver.support.ui import WebDriverWait
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

import scrapy

import mirror0.generic_spider 
from mirror0.afl.ooyala_js_pipeline import init_chrome_driver
from mirror0.afl.afl_fs_pipeline import AflFSPipeline
from mirror0.heraldsun.module0 import HeraldsunItem
from mirror0.sscommon.aux import format_exc, log
from mirror0 import Config

CONFIG_SECTION = "HeraldSun"
PAGE_TIMEOUT = 20

_webdriver = None

def do_login(inst, driver):
    try:
        driver.implicitly_wait(60)
        driver.set_page_load_timeout(60)
        log("Opening login page", DEBUG)
        try:
            driver.get("http://www.heraldsun.com.au/login")
        except TimeoutException as we:
            log("Login page timeout, continuing", INFO)
        cls_name = 'ncenvoy-identity ncenvoy-identity-login'
        xpath = "//iframe[@class='{}']".format(cls_name)
        el = driver.find_element_by_xpath(xpath)
        fname = el.get_attribute("name")
        log("Switching to frame {}".format(fname))
        driver.switch_to.frame(fname)
        driver.find_element_by_id("cam_password").send_keys("infillpaper01")
        driver.find_element_by_id("cam_username").send_keys("christian@ad-hippo.com")
        driver.find_element_by_class_name("button-submit").click()

        """
        xpath = '//p[contains(text(), "Thank you")]' 
        driver.wait.until(EC.presence_of_element_located(
              (By.XPATH, xpath)))
        """
        log("Login submitted")
    except TimeoutException as we:
        log("Web driver: timeout at login", ERROR)
        raise
    except WebDriverException as we:
        log("Web driver: %s" % we.msg, ERROR)
        raise
    except Exception as e:
        format_exc(inst, "__init__", e)
        raise

class HeraldSpider(mirror0.generic_spider.Spider):
    custom_settings =  { "ITEM_PIPELINES" : 
            { 
                'mirror0.heraldsun.module1.HeraldExtractorPipeline' : 543,
                'mirror0.afl.afl_fs_pipeline.AflFSPipeline' : 544,
                'mirror0.generic_spider.text_image_pipeline.TextImagePipeline': 545,
                'mirror0.generic_spider.meta_file_pipeline.MetaFilePipeline': 546,
                'mirror0.heraldsun.herald_spider.NiuxHerald': 547,
                'mirror0.heraldsun.module2.Nwjs': 548,
                'mirror0.news.module0.Linja': 549,
            },
            "DOWNLOADER_MIDDLEWARES" : 
            {
                "mirror0.heraldsun.selenium_middleware.SeleniumMiddleware" : 0,
            }
    }

    name = "heraldsun"
    BASE_DOMAIN = "www.heraldsun.com.au"
    allowed_domains = [BASE_DOMAIN, "idp.news.com.au",]
    BASE_URL = "http://" + BASE_DOMAIN

    _index_file_name = "heraldsun.log"
    _item_class = HeraldsunItem

    HOME_PAGE = BASE_URL

    @classmethod
    def create_start_urls(cls):
        urls = []
        urls += [u for u in str.splitlines(Config.value(CONFIG_SECTION, "start_urls")) if u]
        return urls 

    def phantom_login(self):
        global _webdriver
        if _webdriver: #login once per application run
            self.driver = _webdriver
            log("Reusing logged in webdriver", DEBUG)
        else:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.loadImages"] = "false"
            dcap["phantomjs.page.settings.resourceTimeout"] = "120000"
            _webdriver = webdriver.PhantomJS(executable_path=Config.value(CONFIG_SECTION, "phantomjs_path"), desired_capabilities=dcap)#init_chrome_driver()#
            self.driver = _webdriver
            log("Starting PhantomJS login")
            do_login(self, self.driver)
            self.driver.implicitly_wait(PAGE_TIMEOUT)
            self.driver.set_page_load_timeout(PAGE_TIMEOUT)
            getLogger("selenium.webdriver").setLevel(INFO)


    def __init__(self, **kw):
        mirror0.generic_spider.Spider.__init__(self, **kw)
        self._per_url_regex_xpath = ( 
            (r"video/sport/afl", "//a[@class='vms-list-item module']/@href", ""), 
            (r"more-news", '//div[@class="module-content"]/div/h4/a/@href', "do_use"), #more-stories
            (r"trade-hq", """//div[@class="main-content"]/descendant::div[@class="module-content"]/div/h4/a/@href | """ 
             r"""//div[@class="main-content"]/descendant::div[@class="module-content"]/div/div/h4/a/@href""", "do_use"),
            (r"(/sport/afl/expert-opinion|teams)", '//div[@class="main-content"]/descendant::div[@class="module-content"]/div/h4/a/@href', "do_use"),
            (r"sport/afl[^/]",  # some data is added at the end of request via redirects
                """//div[@class="group item-count-2 top-portrait"]/descendant::h4/a/@href  | """
                """//div[@class="module collection customised-image first-image-316w421h sectionref-news story-block-3x1 story-block-border story-block-has-section force-316-pmnt mpos-1 mrpos-1"]/descendant::h4/a/@href | """
                """//div[@class="item ipos-1 irpos-2"]/descendant::div[contains(@class, "story-block has-video story-has-footer sectionref-sport sbpos")]/descendant::h4/a/@href |"""
                """//ul[@class="related related-content has-section"]/li/a/@href"""
                ,
                "do_use"), 
            
            )
        for url, regex, webdriver in self._per_url_regex_xpath:
            if "do_use" == webdriver:
                self.phantom_login()
                return

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

from mirror0.news import Niux

class NiuxHerald(Niux):
    request_code = "486c0d047bbe4823a12ababd8c14f818"

    def __init__(self):
        super(NiuxHerald, self).__init__()


