
from mirror0.generic_spider import RawExtractorPipeline

class YahooExtractorPipeline(RawExtractorPipeline):
    def __init__(self):
        RawExtractorPipeline.__init__(self)

        self._title_x = "//h1[@class='page-header-title'][@itemprop='headline']/text()"
        self._text_paragraph_x = "//div[@class='article-container'][@itemprop='articleBody']/p/text()"
        self._abstract_paragraph_x = "//div[@class='page-header-abstract']/p/text()"
        self._picture_x = "//img[@class='article-figure-image']/@src"
        self._time_x = "//time[@class='article-byline-time'][@itemprop='datePublished']/@datetime | //time[@class='byline-time']/text()"
        self._time_format_in = ["%B %d, %Y, %I:%M %p",]
        self._time_format_out = "%B %d, %Y, %I:%M %p" 



