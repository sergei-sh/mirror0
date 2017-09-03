""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes: Time conversion functions
"""
from pytz import timezone
import dateutil.parser

def dt_obj_from_iso(isotime_s):
    loc_dt = dateutil.parser.parse(isotime_s)
    return loc_dt

def format_utc_from_localized(loc_dt, format_s):
    datetime_utc = loc_dt.astimezone(timezone("UTC"))
    return datetime_utc.strftime(format_s)
