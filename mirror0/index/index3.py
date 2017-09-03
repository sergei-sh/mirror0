"""
Project: Mirror0
Author: Sergei Shliakhtin xxx.serj@gmail.com
Purpose: Index class implementation 
Comments: Index version rewritten for Python 3. This worth being rewritten in C++
"""

import binascii
import crcmod
from distutils.dir_util import DistutilsFileError, mkpath
from logging import ERROR
import os.path
import struct
import time
from urllib.parse import urlparse, urlunparse

import mirror0
from mirror0.sscommon.config3 import Config
from mirror0.sscommon.aux import log, format_exc

""" Fingerprint size. 2^(-64) is sufficient false positive probability for a single link, 
given link count is magnitude 10^3 and index is through one domain only (resulting at least one error P < 10^(-12) )
"""
CRC_LEN = 8 

def _long_to_bytes(long_val):
    """    
    long_val: Int value, up to CRC_LEN bytes  
    returns: binary representation as bytes
    """
    bytes_list = []
    for i in range(0, CRC_LEN):
        a_byte = long_val % 256
        bytes_list.insert(0, a_byte)
        long_val //= 256
    return struct.pack("B" * CRC_LEN, *bytes_list)

def _bytes_to_long(bytes_val):
    """
    bytes_val: exactly CRC_LEN bytes
    returns: int
    """
    assert len(bytes_val) == CRC_LEN
    return int(binascii.hexlify(bytes_val), base=16)

def _strip_url(url):
    """Unifies resource addresses
    See the unit test for examples
    url: string
    returns: string URL without protocol and trailing chars
    """
    o_var = list(urlparse(url))
    o_var[0] = ""
    return urlunparse(o_var).strip("/")
 
class IndexFingerprintException(Exception):
    pass

class Index:
    """ Manages URL fingerprints for a domain. Loads binary data to memory for efficient comaprison. 
    The user is responsible to call save(). Text log is written for human to preview binary content
    """
    def __init__(self, *, domain):
        """Loads data to memory. Creates index directory if needed and raises DistutilsFileError, OSError
        Raises IdexFingerpringException
        domain - index storage ID
        """
        POLYNOMIAL = 0x1AABBCCDDFFEEDDCC # must be 65 bit long

        self._hashes = set()
        self._crc_fun = crcmod.mkCrcFun(POLYNOMIAL, initCrc=0)

        try:
            # When run from the unit test, index directory path will be tweaked in Config
            file_path =Config.value(mirror0.SECTION_COMMON, "index_directory") 
            mkpath(file_path)

            file_name = domain + ".crc64"
            self._file_path = os.path.join(file_path, file_name)
            with open(self._file_path, "rb") as f:
                data = f.read()
        except (OSError, DistutilsFileError) as e:
            format_exc(self, "Index init failed", e)
            raise
                        
        if len(data) % CRC_LEN:
            msg = "{} is corrupt!".format(self._file_path)
            log(msg, ERROR)
            raise IndexFingerprintException(msg) 

        count = len(data) // CRC_LEN
        for i in range(0, count):
            string_val = data[i*CRC_LEN : (i + 1)*CRC_LEN]
            int_val = _bytes_to_long(string_val)
            self._hashes.update([int_val])
        log("Read {} hashes from {}".format(count, file_name))

        file_name = domain + ".log"
        self._log_file_path = os.path.join(file_path, file_name)
        self.index_log("\n\nSTARTED {}\n".format(time.strftime("%d %b %Y %H:%M:%S")))

    def __len__(self):
        """Records count"""
        return len(self._hashes)            
           
    def has(self, url_str):
        """Checks whether URL string is in index.         
        url_str: URL string. URLs are unified 
        returns: bool
        """
        crc = self._crc_fun(_strip_url(url_str).encode("ascii"))
        return crc in self._hashes

    def add(self, url_str):
        """New URL to index
        url_str: string
        """
        url_str = _strip_url(url_str)

        self.index_log(url_str + "\n")

        crc = self._crc_fun(url_str.encode("ascii"))
        self._hashes.update([crc])

    def save(self):
        """ Writes all data to disc
        """
        try:
            with open(self._file_path, "wb") as out_f:
                for hsh in self._hashes:
                    out_f.write(_long_to_bytes(hsh))
        except OSError as e:
            format_exc(self, "Saving {} failed".format(self._file_path), e)
            raise

    def index_log(self, message):
        """ URLs added in text form are saved to separate file for human reference
        message: string
        """
        try:
            with open(self._log_file_path, "a") as f:
                f.write(message)
        except OSError as e:
            format_exc(self, "Index log write failed {}".format(self._file_path), e)
            raise


