
from scrapy import Item, Field

from mirror0.generic_spider import StateItem

class FoxsportsItem(StateItem):

    raw_text = Field()
    raw_html = Field()
    raw_url = Field() 
    title = Field()
    text = Field()
    pictures = Field()
    time = Field()
    path = Field()
    vlog = Field()
    video_urls = Field()
    out_dir = Field()
    """DEBUG"""
    video_url = Field()
