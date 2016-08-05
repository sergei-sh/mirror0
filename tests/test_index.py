
import logging
import os
import sys
import unittest

sys.path.append("../")

import mirror0.index.index
from mirror0 import Config, Index

class InitOut:
    def __init__(self):
        self.count = -1

DOMAIN = "yahoo"

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

class TestIndex(unittest.TestCase):
    def test_open_empty(self):
        dbg = InitOut()
        mir_idx = Index(DOMAIN, dbg)
        self.assertEqual(dbg.count, 0)

    def test_open_ok(self):
        dbg = InitOut()
        with open(DOMAIN + ".crc64", "wb") as f:
            f.write("abcd0123abcd9999")
        mir_idx = Index(DOMAIN, dbg)
        self.assertEqual(dbg.count, 2)

    def test_open_fail(self):
         with open(DOMAIN + ".crc64", "wb") as f:
             f.write("abcd0123abcd012")
         try:
            mir_idx = Index(DOMAIN)
         except Exception:
            pass
         self.assertEqual('mir_idx' in locals(), False)

    def test_long_string(self):
        print Index._long_string(48)
        print len(Index._long_string(48))

    def test_setsave(self):
        mir_idx = Index(DOMAIN)
        mir_idx.add("test text1")
        mir_idx.add("test text2")
        mir_idx.save()
        with open(DOMAIN + ".crc64", "rb") as f:
            self.assertEqual(len(f.read()), mirror0.index.index.CRC_LEN * 2)

    def test_save_read(self):
        mir_idx = Index(DOMAIN)
        mir_idx.add("test textA")
        mir_idx.add("test textB")
        mir_idx.add("test textC")
        mir_idx.save()
        del mir_idx

        dbg = InitOut()
        mir_idx = Index(DOMAIN, dbg)
        self.assertEqual(dbg.count, 3)
        self.assertEqual(mir_idx.has("test textB"), True)
        self.assertEqual(mir_idx.has("test textC"), True)
        self.assertEqual(mir_idx.has("test textD"), False)

    def test_functional(self):
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
            mir_idx = Index(DOMAIN, dbg)
            print dbg.count
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
        self.assertEqual(STRIPPED, Index._strip_url(u1))
        self.assertEqual(STRIPPED, Index._strip_url(u2))
        self.assertEqual(STRIPPED, Index._strip_url(u3))
    
    @staticmethod
    def clear():
        os.system("find . -regex .*crc64 -exec rm -f {} \;") 

    def setUp(self):
        TestIndex.clear()

    def tearDown(self):
        TestIndex.clear()
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestIndex)
unittest.TextTestRunner(verbosity=2).run(suite)

