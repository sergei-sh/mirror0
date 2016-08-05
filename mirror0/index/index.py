
import binascii
from distutils import dir_util
import struct
from logging import ERROR
import crcmod
import os.path
import time
import urlparse 

import mirror0
from mirror0.sscommon.aux import log, format_exc
from mirror0 import Config

CRC_LEN = 8

class Index:
    def __init__(self, domain, dbg_out=None):
        try:
            POLYNOMIAL = 0x1AABBCCDDFFEEDDCC # must be 65 bit long

            self._debug = 0

            self._hashes = set()
            self._crc_fun = crcmod.mkCrcFun(POLYNOMIAL, initCrc=0)
            self._file_path = ""
            self._log_file_path = ""


            file_path =Config.value(mirror0.SECTION_COMMON, "index_directory") 
            try:
                dir_util.mkpath(file_path)
            except Exception:
                pass

            file_name = domain + ".crc64"
            self._file_path = os.path.join(file_path, file_name)
            with open(self._file_path, "a+b") as f:
                data = f.read()
                if len(data) % CRC_LEN:
                    raise Exception("%s is corrupt!" % file_name)
                count = len(data) / CRC_LEN
                for i in range(0, count):
                    s_val = data[i*CRC_LEN : (i + 1)*CRC_LEN]
                    i_val = Index._string_long(s_val)
                    self._hashes.update([i_val])
                if dbg_out:
                    dbg_out.count = len(self._hashes) 
                log("Read %i hashes from %s" % (count, file_name))

            file_name = domain + ".log"
            self._log_file_path = os.path.join(file_path, file_name)
            with open(self._log_file_path, "a") as f:
                f.write("\n\nSTARTED %s\n" % time.strftime("%d %b %Y %H:%M:%S"))

        except Exception as e:
            format_exc(self, "__init__", e)
            log(self._file_path, ERROR)
            raise

    @staticmethod
    def _long_string(long_val):
        lst = []
        for i in range(0, CRC_LEN):
            byt = long_val % 256
            lst.insert(0, byt)
            long_val //= 256
        return struct.pack("8B", *lst)

    @staticmethod
    def _string_long(long_val):
        return int(binascii.hexlify(long_val), 16)
            
    def has(self, byte_str):
        #self._debug += 1
        #if (self._debug % 3) == 0:
        #    return True

        crc = self._crc_fun(Index._strip_url(byte_str))
        return crc in self._hashes

    @staticmethod
    def _strip_url(url):
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

