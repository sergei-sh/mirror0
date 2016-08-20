
from scrapy import Item, Field
from mirror0.generic_spider import StateItem

class YahooItem(StateItem):
    #def __init__(self, spider=None):
    #    super(YahooItem, self).__init__()

    raw_text = Field()
    raw_html = Field()
    raw_url = Field() 
    title = Field()
    text = Field()
    pictures = Field()
    time = Field()
    path = Field()
    vlog = Field()
