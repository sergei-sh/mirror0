
import os.path

from mirror0.generic_spider import FSCreatorPipeline
from mirror0.afl import AflFSPipeline

class WatodayFSPipeline(FSCreatorPipeline):
    @staticmethod
    def getItemDir(item, spider):
#predefined dir for title page items
        if 'out_dir' in item:
            return os.path.join(item['out_dir'], item['title'])
        else:
#directory from path
            return AflFSPipeline.getItemDir(item, spider)

