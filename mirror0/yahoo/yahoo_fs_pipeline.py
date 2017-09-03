""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from mirror0.generic_spider import FSCreatorPipeline

class YahooFSPipeline(FSCreatorPipeline):
    @staticmethod
    def getItemDir(item, spider):
        return item['title']

