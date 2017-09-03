""" 
Updated: 2016
Author: Sergei Shliakhtin
Contact: xxx.serj@gmail.com
Notes:
"""

import logging
from os.path import join
import os
import sys
import unittest

sys.path.append("../")

from mirror0.sscommon.config3 import Config
Config.enable_debug_mode()

from mirror0.index.index3 import Index, IndexFingerprintException, _long_to_bytes, _bytes_to_long, _strip_url
import mirror0

class InitOut:
    def __init__(self):
        self.count = -1

DOMAIN = "test_domain"
TEST_DIR = Config.value(mirror0.SECTION_COMMON, "index_directory") 
PATH_NAME = join(TEST_DIR, DOMAIN)

print(TEST_DIR)

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

class TestIndex(unittest.TestCase):

    def test_long_string(self):
        self.assertEqual(_long_to_bytes(16711680), b"\x00\x00\x00\x00\x00\xff\x00\x00")
        self.assertEqual(len(_long_to_bytes(16711680)), 8)
        self.assertEqual(_bytes_to_long(b"        "), 0x2020202020202020)
 
    def test_open_empty(self):
        mir_idx = Index(domain=DOMAIN)
        print(len(mir_idx))
        self.assertEqual(len(mir_idx), 0)

    def test_open_ok(self):
        print("writing")
        with open(PATH_NAME + ".crc64", "wb") as f:
            f.write(b"abcd0123abcd9999")
        mir_idx = Index(domain=DOMAIN)
        self.assertEqual(len(mir_idx), 2)

    def test_open_fail(self):
         with open(PATH_NAME + ".crc64", "wb") as f:
             f.write(b"abcd0123abcd012")
         try:
            mir_idx = Index(domain=DOMAIN)
         except IndexFingerprintException:
            pass
         self.assertEqual('mir_idx' in locals(), False)

    def test_setsave(self):
        mir_idx = Index(domain=DOMAIN)
        mir_idx.add("test text1")
        mir_idx.add("test text2")
        mir_idx.save()
        with open(PATH_NAME + ".crc64", "rb") as f:
            self.assertEqual(len(f.read()), mirror0.index.index3.CRC_LEN * 2)

    def test_save_read(self):
        mir_idx = Index(domain=DOMAIN)
        mir_idx.add("test textA")
        mir_idx.add("test textB")
        mir_idx.add("test textC")
        mir_idx.save()
        del mir_idx

        dbg = InitOut()
        mir_idx = Index(domain=DOMAIN)
        self.assertEqual(len(mir_idx), 3)
        self.assertEqual(mir_idx.has("test textB"), True)
        self.assertEqual(mir_idx.has("test textC"), True)
        self.assertEqual(mir_idx.has("test textD"), False)

    def test_functional(self):
        with open(PATH_NAME + ".crc64", "wb") as f:
            pass

        str_d = []
        with open("test_in.txt", "r") as f:
            str_d = f.readlines()
        not_present = set(str_d)
        present = set()
        count = len(str_d)

        def check(pres, not_pres, idx):
            for s in pres:
                self.assertEqual(idx.has(s), True)
            for s in not_pres:
                self.assertEqual(idx.has(s), False)

        j = 2
        while len(not_present):
            dbg = InitOut()
            mir_idx = Index(domain=DOMAIN)
            check(present, not_present, mir_idx)

            for _ in range(0, j % 10):
                if not len(not_present): break
                s = not_present.pop()
                mir_idx.add(s)
                present.update([s])
            j += 7
            check(present, not_present, mir_idx)
            mir_idx.save()
            del mir_idx

    def test_strip_url(self):
        u1 = "http://d1.d2/path"
        u2 = "https://d1.d2/path/"
        u3 = "d1.d2/path/#"
        STRIPPED = "d1.d2/path"
        self.assertEqual(STRIPPED, _strip_url(u1))
        self.assertEqual(STRIPPED, _strip_url(u2))
        self.assertEqual(STRIPPED, _strip_url(u3))
    
    @staticmethod
    def clear():
        with open(PATH_NAME + ".crc64", "wb") as f:
            pass

    def setUp(self):
        #create dir
        TestIndex.clear()

    def tearDown(self):
        pass
        #TestIndex.clear()

#suite = unittest.TestLoader().loadTestsFromTestCase(TestIndex)
#unittest.TextTestRunner(verbosity=2).run(suite)

