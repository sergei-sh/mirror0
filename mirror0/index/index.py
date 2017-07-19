"""
Project: Mirror0
Author: Sergei Shliakhtin xxx.serj@gmail.com
Purpose: Index class implementation 
Comments: This worth being rewritten in C++
"""

import binascii
import crcmod
from distutils import dir_util
from logging import ERROR
import os.path
import struct
import time
import urlparse 

import mirror0
from mirror0 import Config
from mirror0.sscommon.aux import log, format_exc

""" Fingerprint size. 2^(-64) is sufficient false positive probability for a single link, 
given link count is magnitude 10^3 and index is through one domain only (resulting at least one error P < 10^(-12) )
"""
CRC_LEN = 8

class IndexFingerprintException(Exception):
    pass

class Index:
    """ Manages URL fingerprints for a domain. Loads binary data to memory for efficient comaprison. 
    The user is responsible to call save(). Text log is written to preview binary content
    """
    def __init__(self, domain):
        """Loads data to memory. Creates index directory if needed and raises DistutilsFileError if failed.
        Raises IdexFingerpringException

        domain - index storage ID
        """
        try:
            POLYNOMIAL = 0x1AABBCCDDFFEEDDCC # must be 65 bit long

            self._debug = 0

            self._hashes = set()
            self._crc_fun = crcmod.mkCrcFun(POLYNOMIAL, initCrc=0)

            # When run from the unit test, index directory path will be tweaked in Config
            file_path =Config.value(mirror0.SECTION_COMMON, "index_directory") 
            dir_util.mkpath(file_path)

            file_name = domain + ".crc64"
            self._file_path = os.path.join(file_path, file_name)
            with open(self._file_path, "a+b") as f:
                data = f.read()
                if len(data) % CRC_LEN:
                    raise IndexFingerprintException("%s is corrupt!" % file_name)
                count = len(data) / CRC_LEN
                for i in range(0, count):
                    string_val = data[i*CRC_LEN : (i + 1)*CRC_LEN]
                    int_val = Index._string_long(string_val)
                    self._hashes.update([int_val])
                log("Read %i hashes from %s" % (count, file_name))

            file_name = domain + ".log"
            self._log_file_path = os.path.join(file_path, file_name)
            # Rewrite through centralized logging
            with open(self._log_file_path, "a") as f:
                f.write("\n\nSTARTED %s\n" % time.strftime("%d %b %Y %H:%M:%S"))

        except IndexFingerprintException as e:
            format_exc(self, "__init__", e)
            log(self._file_path, ERROR)
            raise

    def __len__(self):
        """Records count"""
        return len(self._hashes)            

    @staticmethod
    def _long_string(long_val):
        """Int value to binary representation as bytes"""
        lst = []
        for i in range(0, CRC_LEN):
            byt = long_val % 256
            lst.insert(0, byt)
            long_val //= 256
        return struct.pack("8B", *lst)

    @staticmethod
    def _string_long(long_val):
        """From binary bytes to int"""
        return int(binascii.hexlify(long_val), 16)
            
    def has(self, byte_str):
        """Checks whether URL string is in index. 
        Urls are unified to match by hostname and path only
        """
        crc = self._crc_fun(Index._strip_url(byte_str))
        return crc in self._hashes

    @staticmethod
    def _strip_url(url):
        """Urls are unified to match by hostname and path only
        See the unit test for examples
        """
        o = list(urlparse.urlparse(url))
        o[0] = ""
        return urlparse.urlunparse(o).strip("/")

    def add(self, byte_str):
        byte_str = Index._strip_url(byte_str)

        try:
            f = open(self._log_file_path, "a")
            f.write(byte_str + "\n")
        except Exception as e:
            log("Index log write failed %s" % str(e), ERROR)

        crc = self._crc_fun(byte_str)
        self._hashes.update([crc])

    def save(self):
        try:
            f = open(self._file_path, "wb")
            for hsh in self._hashes:
                f.write(Index._long_string(hsh))
            f.close()
        except Exception as e:
            log("Saving %s failed: %s" % (self._file_path, str(e)))

