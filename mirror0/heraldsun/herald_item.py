""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from scrapy import Field
from mirror0.news.module0 import NewsItem

class HeraldsunItem(NewsItem):
    heraldsun_urls = Field()
