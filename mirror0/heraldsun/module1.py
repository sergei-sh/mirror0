
from mirror0.news.module1 import NewsExtractorPipeline


class HeraldExtractorPipeline(NewsExtractorPipeline):

    def __init__(self):
        NewsExtractorPipeline.__init__(self)
        self._title_x = """//div[@class="tg-tlc-storyheader_titlewrapper"]/h1[@itemprop="headline"]/text() """
        self._text_paragraph_x = '//div[@class="tg-tlc-storybody cf"]/descendant::p/text() |  //article[@class="story-content"]/descendant::p/text()'
        self._abstract_paragraph_x = None
        self._picture_x = """//img[@class="atom-imagecaption_img"]/@src | //article[@class="story-content"]/descendant::figure/img/@src """

