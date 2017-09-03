""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

import scrapy
from scrapy import Item, Field
 
class StateItem(scrapy.Item):
    """Reports its success state to the spider status dict"""

    def __init__(self, spider):
        super(StateItem, self).__init__(self)
        self._spider = spider

    def start(self, state_id):
        self._spider.start_state(self['raw_url'], state_id)

    def finish(self, state_id):
        self._spider.finalize_state(self['raw_url'], state_id)

    def started_states(self):
        return self._spider.started_states(self['raw_url'])

    def __repr__(self):
        return ""

    raw_url = Field() 
