""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

from logging import ERROR
from mirror0.sscommon.aux import log

class ObjectStateIndicators(object):
    """Allows to track multiple states of the item.
       Each state is a string ID which should be "started" then "ended" on an item.
       At the end reports all states which can be written to log, to see which states (pipelines)
       are incomplete
    """

    def __init__(self):
        self.__started = []
        self.__finished = []

    def start(self, obj_id):
        self.started.append(obj_id)

    def finish(self, obj_id):
        assert obj_id in self.__started
        self.finished.append(obj_id)

    @property
    def started(self):
        return self.__started

    @property 
    def finished(self):
        return self.__finished

    @property
    def incomplete(self):
        return set(self.__started) - set(self.__finished)

    def __str__(self):
        obj_states = self
        try:
            started_str = str()
            for s in obj_states.started:
                started_str = started_str + s + " " 

            finished_str = str()
            for s in obj_states.finished:
                finished_str = finished_str + s + " "

            return "{:<30} -> {:<30}".format(started_str, finished_str)
        except TypeError:
            log("format_string_indicators TypeError", ERROR)
            raise
