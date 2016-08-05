
import argparse
from distutils import dir_util
import logging
import logging.config
import os
import sys
from subprocess import call
from twisted.internet import reactor

os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "mirror0.settings") 

from scrapy.crawler import CrawlerRunner #CrawlerProcess
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy import signals

CONFIG_FILE = "mirror0.ini"

import mirror0
from mirror0 import Config
from mirror0.foxsports.foxsports_spider import FoxsportsSpider
from mirror0.watoday.watoday_spider import WatodaySpider
from mirror0.yahoo.yahoo_spider import YahooSpider
from mirror0.afl import AflSpider
import mirror0.afl.afl_spider
from mirror0.wb import WbSpider

def init_logging():
    try:
        logdir = Config.value(mirror0.SECTION_COMMON, "log_directory")
        #cmdline = "sed 's|~LOGDIR~|%s|g' loggers.conf > loggers.tmp" % logdir
        #os.system(cmdline)
        try:
            dir_util.mkpath(logdir)
        except Exception as err:
            if hasattr(err, 'errno') and 17 == err.errno:
                pass 
        #logging.config.fileConfig("loggers.tmp")
        fh = logging.FileHandler(os.path.join(logdir, "console.log"))
        fh.setFormatter(logging.Formatter("(%(module)s.%(funcName)s) [%(levelname)s]: %(message)s"))
        fh.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(fh)
    except Exception as err:
        print "Logging initialization failed: %s" % str(err)
        sys.exit(1)

class SequentialRunner(object):
    
    def __init__(self, spider_cls, urls, proc, **kwargs):
        self._urls = urls
        self._process = proc
        self._spider_cls = spider_cls
        self._kwargs = kwargs

    def next(self):        
        self._process.crawl(self._spider_cls, start_url=self._urls.pop(0), **self._kwargs)
        
        for crawler in self._process.crawlers:
            crawler.signals.connect(self.spider_finished, signal=signals.spider_closed)
            #crawler.configure()

    def spider_finished(self):
        if self._urls:
            self.next()    

def run():

    init_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("spider_name", type=str)
    parser.add_argument("--noindex", help="Scrape all no matter what's already saved", action="store_true")
    parser.add_argument("--lessvid", help="Suppress most Ooyala1 videos (handy for testing other types)", action="store_true")
    parser.add_argument("--firstpage", help="", action="store_true")
    keys = parser.parse_args()
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    keys_args = { 'no_index':keys.noindex, 'less_vid':keys.lessvid, 'first_page':keys.firstpage }
    if "watoday" == keys.spider_name:
        urls = WatodaySpider.create_start_urls() 
        WatodaySpider.init_idx_log()
        runner = SequentialRunner(WatodaySpider, urls, process, **keys_args)
        runner.next()
    elif "yahoo" == keys.spider_name:
        urls = YahooSpider.create_start_urls() 
        YahooSpider.init_idx_log()
        process.crawl(YahooSpider, start_url=urls[0])
    elif "afl" == keys.spider_name:
        urls = AflSpider.create_start_urls() 
        AflSpider.init_idx_log()
        runner = SequentialRunner(AflSpider, urls, process, **keys_args)
        runner.next()
    elif "wb" == keys.spider_name:
        urls = WbSpider.create_start_urls()
        WbSpider.init_idx_log()
        runner = SequentialRunner(WbSpider, urls, process, **keys_args)
        runner.next()
    elif "foxsports" == keys.spider_name:
        urls = FoxsportsSpider.create_start_urls()
        FoxsportsSpider.init_idx_log()
        runner = SequentialRunner(FoxsportsSpider, urls, process, **keys_args)
        runner.next()
    else:
        logging.log(logging.ERROR, "Unknown spider name")

    process.start()

run()
