
import json
from logging import ERROR, DEBUG, WARNING

import logging
import json
import os
import os.path
import shutil
import subprocess
import time

from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

import mirror0
from mirror0 import Config
from mirror0 import generic_spider
from mirror0 import SECTION_COMMON
from mirror0.sscommon.aux import log, format_exc
from mirror0 import Config

NO_VIDEO = False

class StreamPipeline(object):

    STATE_ID = "VID"
    STATE_NOVID = "NOVID"

    __downloaded_files = {}

    def __init__(self):
        self._sub_proc = []
        self._no_duplicates = int(Config.value(mirror0.SECTION_COMMON, "no_duplicate_videos"))
        pass 

    def process_item(self, item, spider):
        if NO_VIDEO or ('skip_video' in item and item['skip_video']):
            return item

        spider.video_processor = self

        try:
            #check if already downloaded (or tried to) and link to previously saved path
            if self._no_duplicates:
                video_fname = self.get_video_filename(item)
                if video_fname:
                    if video_fname in self.__downloaded_files:
                       ln_to = os.path.join(self.__downloaded_files[video_fname], video_fname)
                       #if os.path.isfile(ln_to):
                       ln_from = os.path.join(item['path'], video_fname)
                       rln = self._call(["ln", "-s", "-f", "--no-dereference", ln_to, ln_from])
                       url = item['raw_url']
                       log("Linking {0} to {1} for {2}".format(ln_from, ln_to, url), DEBUG)
                       spider.start_state(url, self.STATE_ID)
                       spider.finalize_state(url, self.STATE_ID)
                       return item#do not download
                    else:
                        #remember fname immediately, if not done before. don't wanna wait results
                        #making things more complex. want to exclude duplicates of not-yet-finished videos.
                        self.__downloaded_files[video_fname] = item['path']
                        #print "added {0}".format(video_fname)

            logfile_path = item['vlog'].file_path
            logfile = open(logfile_path, "w", 0)

            timeout = get_project_settings().get('DOWNLOAD_TIMEOUT', 30)
            data_dir = item['path']
            cmdline = "youtube-dl --no-warnings "
            if int(Config.value(mirror0.SECTION_COMMON, "hls_prefer_native")):
                cmdline += "--hls-prefer-native "
            cmdline += "--no-part --socket-timeout {0} ".format(timeout)
            cmdline += "-o '%s" % data_dir  
            cmdline += "/%(title)s.%(ext)s' "
            cmdline += item['raw_url']
            logfile.write(cmdline + "\n")

            self._sub_proc.append(
                (subprocess.Popen([cmdline], stdout=logfile.fileno(), stderr=logfile.fileno(), shell=True), #stderr=subprocess.STDOUT,
                 logfile,
                 logfile_path,
                 item['raw_url'],),
                )

            #for key, value in logging.Logger.manager.loggerDict.iteritems():

        except Exception as e:
            format_exc(self, "porcess_item", e)

        return item

    """do not download yet but only enquire video file name in advance"""
    def get_video_filename(self, item):
        try:
            cmdline = "youtube-dl --no-warnings --get-filename -o '%(title)s.%(ext)s' "
            cmdline += item['raw_url']
            process = subprocess.Popen([cmdline], stdout=subprocess.PIPE, stderr=None, shell=True)
            out_err_tpl = process.communicate()
            return out_err_tpl[0].strip()

        except Exception as e:
            format_exc(self, "get_video_filename", e)

    @staticmethod
    def _call(arglst):
        try:
            subprocess.check_call(arglst, stdout=None)
        except subprocess.CalledProcessError as e:
            return e.returncode
        except Exception as e:
            log("subporcess.check_call failed %s" % str(e), ERROR)
            return 2
        return 0
 
    def wait_all_finished(self, spider):
        try:
            log("Waiting for video processes to complete...")
            i = len(self._sub_proc)
            for process, logfile, logfile_path, url in self._sub_proc:
                print "Left %i" % (i)
                if self._no_duplicates:
                    tail_proc = subprocess.Popen(["tail", "-f", "-n", "1", logfile_path], stdout=None, stderr=None)
                process.communicate()
                #process.wait()
                if self._no_duplicates:
                    tail_proc.terminate()
                logfile.close()
                # downloaded successfully
                if 0 == process.returncode:
                    spider.start_state(url, self.STATE_ID)
                    spider.finalize_state(url, self.STATE_ID)
                # return code 1 can indicate both no video on page or not supported page
                elif 1 == process.returncode:
                    # check_call accepts a list of arguments only
                    grepr = StreamPipeline._call(["grep", "ERROR.*Unsupported", logfile_path])
                    if 0 == grepr:
                        spider.start_state(url, self.STATE_NOVID)
                        spider.finalize_state(url, self.STATE_NOVID)
                    else:
                        grepr = StreamPipeline._call(["grep", "ERROR.*content ID", logfile_path])
                        spider.start_state(url, self.STATE_ID)
                        if 0 == grepr:
                            log("Content id error %s" % url, DEBUG)
                        else:
                            grepr = StreamPipeline._call(["grep", "ERROR.*timed out", logfile_path])
                            if 0 == grepr :
                                log("Ydl video timed out {0}".format(url), WARNING)   
                            elif 1 == grepr:
                                log("Log state is not known %s" % (url), WARNING)
                            else:
                                log("Grep return code %i %s" % (grepr, url), WARNING)
                elif -2 == process.returncode:
                    #interruped by user
                    spider.start_state(url, self.STATE_ID)
                    pass
                else:
                    #started state without later finalizing means fail
                    spider.start_state(url, self.STATE_ID)
                    log("Youtube-dl return code %i %s" % (process.returncode, url), WARNING)
                i -= 1
            self._sub_proc[:] = []
        except Exception as e:
            format_exc(self, "wait_all_finished", e)
            raise





