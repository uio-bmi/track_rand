import unittest
import os
import sys
from numpy import array, memmap

from gold.track.SmartMemmap import SmartMemmap
from test.util.FileUtils import removeFile
from test.util.Asserts import AssertList

import gold.track.SmartMemmap
gold.track.SmartMemmap.MEMMAP_BIN_SIZE = 100

class TestSmartMemmap(unittest.TestCase):
    def setUp(self):
        self.stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')

        self._fn = os.tmpnam()
        self._m = memmap(self._fn, dtype='int32', mode='w+', shape=190)
        self._m[0:190] = array(range(190))
        self._m.flush()
        
        self._sm = SmartMemmap(self._fn, elementDim=None, dtype='int32', dtypeDim=1, mode='r')
        
    def tearDown(self):
        sys.stderr = sys.stderr

        removeFile(self._fn)
        
    def testSlice(self):
        m = self._m
        sm = self._sm
        
        AssertList(m[0:0], sm[0:0], self.assertEqual)
        AssertList(m[0:100], sm[0:100], self.assertEqual)
        AssertList(m[10:20], sm[10:20], self.assertEqual)
        AssertList(m[90:110], sm[90:110], self.assertEqual)
        AssertList(m[110:120], sm[110:120], self.assertEqual)
        
    def testIndex(self):
        m = self._m
        sm = self._sm
        
        self.assertEqual(m[0], sm[0])
        self.assertEqual(m[11], sm[11])
        self.assertEqual(m[99], sm[99])
        self.assertEqual(m[111], sm[111])
        self.assertEqual(m[189], sm[189])
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestSmartMemmap().debug()
    unittest.main()
