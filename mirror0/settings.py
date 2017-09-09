# -*- coding: utf-8 -*-

""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: Large DOWNLOAD_WARNSIZE because we're downloading large videos
"""

# Scrapy settings for mirror0 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

SPIDER_LOADER_CLASS = "scrapy.spiderloader.SpiderLoader"

LOG_LEVEL="DEBUG"

BOT_NAME = 'mirror0'

SPIDER_MODULES = ["mirror0.afl", "mirror0.foxsports", "mirror0.heraldsun", "mirror0.news", "mirror0.watoday", "mirror0.wb", "mirror0.yahoo"]
NEWSPIDER_MODULE = 'mirror0.yahoo'

DOWNLOAD_DELAY=0.8
RANDOMIZE_DOWNLAOD_DELAY=True
DOWNLOAD_TIMEOUT=240
CONCURRENT_REQUESTS=12
DOWNLOAD_WARNSIZE=5000000000

REDIRECT_ENABLED=True
REDIRECT_MAX_TIMES=8

#LOG_FILE = "mirror0.log"

#DOWNLOADER_MIDDLEWARES = {
#    scrapy.downloadermiddlewares.redirect.RedirectMiddleware : 543,
#}





# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mirror0 (+http://www.yourdomain.com)'

# Configure maxi    mum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'mirror0.middlewares.MyCustomSpiderMiddleware': 543,
#}


# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}


# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
