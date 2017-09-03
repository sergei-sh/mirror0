""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from scrapy import Item, Field

from mirror0.generic_spider import StateItem

class WatodayItem(StateItem):

    raw_text = Field()
    raw_html = Field()
    raw_url = Field() 
    title = Field()
    text = Field()
    pictures = Field()
    time = Field()
    path = Field()
    vlog = Field()
    skip_video = Field()
    twitter_data = Field()
    out_dir = Field()
