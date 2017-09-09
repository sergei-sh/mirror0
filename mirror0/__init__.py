
import logging

#TODO: uncomment
from sscommon.config import Config 
from index.index import Index

#_all_ = ["generic_spider",]

SECTION_COMMON = "Common"

from init_logging import init_logging

class MirrorException(Exception):
    pass


