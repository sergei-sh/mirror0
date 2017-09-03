""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from scrapy import Field

from mirror0.generic_spider import StateItem

class AflItem(StateItem):

    raw_html = Field()
    raw_text = Field()
    title = Field()
    text = Field()
    pictures = Field()
    time = Field()
    path = Field()
    ooyala_video_ids = Field()
    ooyala_urls = Field()
    vlog = Field()
    twitter_video_ids = Field()
    twitter_data = Field()

