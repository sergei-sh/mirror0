RUN:
python mirror0.py [spider_name] 
Example:
python mirror0.py afl
python mirror0.py yahoo
Ver 1.1-b2: 
    -only one spider at a time supported
AFL:
Each category link should be added to mirror0.ini: [Afl]/start_urls
Spider names:
afl yahoo wb watoday foxsports

Command line switches:
    --noindex - don't readd/add to index
    --lessvid - disable downloading most ooyala1 videos, useful for testing other types

You need python 2.7 (3.* will not work)

INSTALLATION:
1) cd to source directory
2) ./setup.sh HOUR MINUTE
example: ./setup.sh 13 23
where 
HOUR,MINUTE - time to run daily
3) go to $HOME/.mirror0 and edit mirror0.ini to change output data and log directories 
4) see current_*.log file as the output for the scheduled job


SETTINGS:
mirror0.ini - output/log directories and url to start with

Logs:
%LOGDIR%/linkwise.log - results per URL
%LOGDIR%/stream/* - per URL youtube-dl logs
.mirror0/sports.yahoo.com.log - links added to index. This file is for user reference only, change or delete does not affect anything

