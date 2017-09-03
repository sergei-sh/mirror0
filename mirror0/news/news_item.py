""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from scrapy import Item, Field

from mirror0.generic_spider import StateItem
from mirror0.yahoo import StreamPipeline

class NewsItem(StateItem):

    raw_text = Field()
    raw_html = Field()
    raw_url = Field() 
    title = Field()
    text = Field()
    pictures = Field()
    time = Field()
    path = Field()
    vlog = Field()
    ooyala_id = Field()
    playlist_url = Field()

class Linja(StreamPipeline):
    """THIS SHOULD BE RENAMED/MOVED"""
    def __init__(self):
        super(Linja, self).__init__()
        self.download_url_field = "playlist_url"


