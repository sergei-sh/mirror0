""" 
Updated: 2017
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: 

The application entry point. Chooses an appropriate spider and runs it sequentially for each category.
TODO: investigate constructor run
"""

import argparse
from logging import DEBUG, ERROR
import os

os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "mirror0.settings") 

from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.utils.project import get_project_settings
from scrapy import signals

from mirror0 import init_logging, MirrorException
from mirror0.sscommon import log

class SequentialRunner(object):
    """Utilize CrawlerProcess interface to run the spider for each category url.
       Make the next category spider run, after the current one is done.
    """
    
    def __init__(self, proc, name, **kwargs):
        log("SequentialRunner __init__", DEBUG)
        self._process = proc
        self._kwargs = kwargs
        self._spider_name = name
        self._spider_cls = self._process.spider_loader.load(self._spider_name)

        self._urls = self._spider_cls.create_start_urls()
        if not self._urls:
            raise MirrorException("Spider created empty url list")

    def crawl_next(self):        
        """Pop next category from url list and run the next spider with this url"""

        new_crawler = Crawler(self._spider_cls)
        self._process.crawl(new_crawler, start_url=self._urls.pop(0), **self._kwargs)
        new_crawler.signals.connect(self.spider_finished, signal=signals.spider_closed)
        
    def spider_finished(self, spider, reason):
        """Proceed to the next category url"""

        log("SequentialRunner spider_finished", DEBUG)
        if self._urls:
            self.crawl_next()    

class CommandAccumulator(object):
    """Accept cleanup callables from multiple spiders to be run at the application end even if interrupted
    E.g. webdriver applications are run only once and only if needed then closed after all spiders done"""
    
    def __init__(self):
        self._commands = []

    def add_command(self, command):
        """Add a callable object"""
        assert command.__call__, "Command should be callable"
        self._commands.append(command)

    def run_commands(self):
        """Run everything"""
        for command in self._commands:
            command()

def run():
    """Run spider according to the name argument, pass all other arguments into spider's constructor"""

    init_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("spider_name", type=str)
    parser.add_argument("--noindex", help="Scrape all no matter what's already saved", action="store_true")
    parser.add_argument("--lessvid", help="Suppress most Ooyala1 videos (handy for testing other types)", action="store_true")
    parser.add_argument("--firstpage", help="Scrape the first page only from each category", action="store_true")
    keys = parser.parse_args()

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    cleaner = CommandAccumulator()
    
    keys_args = { 'no_index':keys.noindex, 'less_vid':keys.lessvid, 'first_page':keys.firstpage, 'object_cleaner':cleaner }
    runner = SequentialRunner(process, keys.spider_name, **keys_args)
    runner.crawl_next()
    log("CrawlerProcess start", DEBUG)
    process.start()

    # Everything is finished here,so do cleanup
    cleaner.run_commands()

run()
