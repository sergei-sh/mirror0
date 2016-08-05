
from scrapy.item import Field
from mirror0.generic_spider import StateItem

class WbItem(StateItem):

    raw_html = Field()
    title = Field()
    text = Field()
    pictures = Field()
    time = Field()
    path = Field()
    ooyala_video_ids = Field()
    ooyala_urls = Field()
    vlog = Field()

