
from logging import ERROR, DEBUG, WARNING, INFO
import logging
import os.path
from pyvirtualdisplay.smartdisplay import SmartDisplay
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

import scrapy
from mirror0 import Config
from mirror0 import SECTION_COMMON
from mirror0.afl.ooyala1_pipeline import Ooyala1Pipeline, OOYALA_JS_ID
from mirror0.generic_spider import MediaPipelineEx
from mirror0.generic_spider import Spider
from mirror0.sscommon.aux import log, format_exc

display = SmartDisplay(visible=0, bgcolor="black")
display.start()

class OoyalaJSPipeline(MediaPipelineEx):
    STATE_ID = OOYALA_JS_ID

    def __del__(self):
        self.__cleanup() 

    def close_spider(self, spider):
        self.__cleanup()

    def __cleanup(self):
        try:
            self.driver.close()
            del self.driver
        except AttributeError:
            pass

    def __init__(self):
        super(self.__class__, self).__init__(dont_filter=True)
        logging.getLogger("selenium").setLevel(logging.INFO)

    def open_spider(self, spider):
        super(self.__class__, self).open_spider(spider)

        chrome_options = Options()
        chrome_options.add_argument("--disable-bundled-ppapi-flash")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--disable-webaudio")
        chrome_options.add_argument("--mute-audio")
        #chrome_options.add_argument("--no-startup-window")
        prefs = {}
        prefs["plugins.plugins_disabled"] = ["Adobe Flash Player", "Shockwave Flash"]
        prefs["profile.managed_default_content_settings.images"] = 2
        #prefs["profile.managed_default_content_settings.media_stream"] = 2
        chrome_options.add_experimental_option("prefs", prefs)

        path = Config.value(SECTION_COMMON, "chromedriver_path")
        if path:
            log("Chromedriver path: %s" % path, INFO)
            self.driver = webdriver.Chrome(executable_path=path, chrome_options=chrome_options)
        else:
            self.driver = webdriver.Chrome(chrome_options=chrome_options)

        self.driver.wait = WebDriverWait(self.driver, 50)


    def get_media_requests(self, item, info):
        try:
            url = item['raw_url']

            if OOYALA_JS_ID not in item.started_states():
                log("Ooyala JS skipping %s" % item['raw_url'], DEBUG)
                return
            log("OoyalaJS: type2 video extracting url %s" % url, INFO)

            self.driver.get(url)
            VID_X = "//div[contains(@class, 'video')]/div[contains(@class, 'ooyala-video')]/descendant::video[@class='video'][contains(@src, 'http')]"
            self.driver.wait.until(EC.presence_of_element_located(
                  (By.XPATH, VID_X)))
            log("OoyalaJS: successfully extracted %s" % url, DEBUG)
            el_list = self.driver.find_elements_by_xpath(VID_X)
            assert not item['ooyala_urls'], "Really type 2"
            for el in el_list:
                item['ooyala_urls'].append(el.get_attribute("src"))
            log(item['ooyala_urls'], DEBUG)

            if not item['ooyala_urls'] or not item['ooyala_urls'][0]:
                with open("zzz1.html", "w") as f:
                     f.write(self.driver.page_source.encode("ascii", "ignore"))

            #delegate video urls downloading to ooyala1
            return Ooyala1Pipeline.yield_requests(self, item, 'ooyala_urls')
        except TimeoutException as we:
            print "written"
            log("Web driver: timeout")
            item['vlog']("Ooyala JS: timeout")
        except WebDriverException as we:
            log("Web driver: %s" % we.msg, ERROR)
            item['vlog']("Ooyala JS: " + we.msg)
        except Exception as e:
            format_exc(self, "get_media_requests", e)
            item['vlog']("Ooyala JS: " + str(e))

    def media_downloaded(self, response, request, info):
        Ooyala1Pipeline.handle_downloaded(self, response) 

    def media_failed(self, failure, request, info):
        Ooyala1Pipeline.handle_failed(self, failure, request)


