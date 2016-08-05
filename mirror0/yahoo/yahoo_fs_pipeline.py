
from mirror0.generic_spider import FSCreatorPipeline

class YahooFSPipeline(FSCreatorPipeline):
    @staticmethod
    def getItemDir(item, spider):
        return item['title']

