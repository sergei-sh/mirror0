
import logging 
from logging import ERROR, DEBUG, WARNING, INFO
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

from mirror0.afl.ooyala1_pipeline import Ooyala1Pipeline
from mirror0.afl.ooyala_js_pipeline import OoyalaJSPipeline, init_chrome_driver  
from mirror0.generic_spider import MediaPipelineEx
from mirror0.heraldsun.herald_spider import do_login
from mirror0.news.news_spider import Niux
from mirror0.sscommon.aux import log, format_exc

_driver = None

def _clean_if_need():
    global _driver
    try:
        _driver.close() 
        del _driver
    except NameError:
        pass

TIMEOUT = 360 

class Nwjs(MediaPipelineEx):
    STATE_ID = Niux.STATE_TYPE2
    VID_X = "//video[contains(@src, 'http')]"

    def __init__(self, *args, **kw):
        kw["dont_filter"] = True
        logging.getLogger("selenium").setLevel(DEBUG)
        super(Nwjs, self).__init__(*args, **kw)

    #def close_spider(self, spider):
    #    del self.driver

    def open_spider(self, spider):
        #super(self.Nwjs, self).open_spider(spider)
        MediaPipelineEx.open_spider(self, spider)
        spider._object_cleaner.add_command(_clean_if_need)
        global _driver
        if not _driver:
            _driver = init_chrome_driver(TIMEOUT)
            log("Starting Chromedriver login")
            do_login(self, _driver)

        #self.driver = _driver

    def _clean_if_need(self):
        global _driver
        try:
            _driver.close() 
            del _driver
        except AttributeError:
            pass

    def get_media_requests(self, item, info):
        try:
            url = item['raw_url']
            if self.STATE_ID not in item.started_states():
                log("NW JS skipping %s" % url, DEBUG)
                return
            log("NW JS: type2 video extracting url %s" % url, INFO)

            global _driver
            _driver.implicitly_wait(40)
            _driver.set_page_load_timeout(40)

            try:
                print "getting"
                _driver.get(url)
            except TimeoutException as we:
                log("Nwjs: Web driver expected timeout")

            _driver.implicitly_wait(TIMEOUT)
            _driver.set_page_load_timeout(TIMEOUT)
 
            #with open("zzz1.html", "w") as f:
            #    f.write(_driver.page_source.encode("ascii", "ignore"))

            _driver.wait.until(EC.presence_of_element_located(
                  (By.XPATH, self.VID_X)))

            #with open("zzz2.html", "w") as f:
            #    f.write(_driver.page_source.encode("ascii", "ignore"))

            log("OoyalaJS: successfully extracted %s" % url, DEBUG)
            el_list = _driver.find_element_by_xpath(self.VID_X)
            item['playlist_url'] = el_list.get_attribute("src")
            log(item['playlist_url'], DEBUG)

            return item
            """
            item['heraldsun_urls'] = []
            for el in el_list:
                item['heraldsun_urls'].append(el.get_attribute("src"))
            log(item['heraldsun_urls'], DEBUG)

            

            #delegate video urls downloading to ooyala1
            return Ooyala1Pipeline.yield_requests(self, item, 'heraldsun_urls')
            """
        except TimeoutException as we:
            with open("heraldtimeout.html", "w") as f:
                f.write(_driver.page_source.encode("ascii", "ignore"))

            log("Nwjs: Web driver: timeout")
            item['vlog']("Ooyala JS: timeout")
        except WebDriverException as we:
            log("Nwjs: Web driver: %s" % we.msg, ERROR)
            item['vlog']("Ooyala JS: " + we.msg)
        except Exception as e:
            format_exc(self, "get_media_requests", e)
            item['vlog']("Nwjs: " + str(e))

    def media_downloaded(self, response, request, info):
        Ooyala1Pipeline.handle_downloaded(self, response) 

    def media_failed(self, failure, request, info):
        Ooyala1Pipeline.handle_failed(self, failure, request)

