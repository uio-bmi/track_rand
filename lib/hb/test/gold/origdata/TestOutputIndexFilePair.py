import unittest
from numpy import memmap, array
import os
import sys

import gold.util.CompBinManager
import gold.origdata.OutputIndexFilePair

from gold.origdata.GenomeElement import GenomeElement
from test.util.Asserts import AssertList
from test.util.FileUtils import removeFile

class DummyFile(object):
    def __init__(self, contents):
        self._contents = array(contents)
        
    def getContents(self):
        return self._contents

class TestOutputIndexFilePair(unittest.TestCase):
    def setUp(self):
        self.stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')

        self.path = os.path.dirname(os.tempnam())
        self.prevCompBinSize = gold.util.CompBinManager.COMP_BIN_SIZE
        gold.util.CompBinManager.COMP_BIN_SIZE = 100
        
    def tearDown(self):
        sys.stderr = sys.stderr

        self._removeFiles()
        gold.util.CompBinManager.COMP_BIN_SIZE = self.prevCompBinSize
        
    def _removeFiles(self):
        removeFile(self.path + os.sep + 'leftIndex.int32')
        removeFile(self.path + os.sep + 'rightIndex.int32')
        
    def _assertIndexFile(self, contents, prefix):
        fn = self.path + os.sep + prefix + '.int32'
        
        self.assertTrue(os.path.exists(fn))
        fileContents = [el for el in memmap(fn, 'int32', mode='r')]
        AssertList(contents, fileContents, self.assertEqual)
        
    def _assertWriteIndexes(self, leftContents, rightContents, startList, endList, endIndex):
        prefixList = (['start'] if startList!=[] else []) + (['end'] if endList!=[] else [])
        from gold.origdata.OutputIndexFilePair import OutputIndexFilePair
        of = OutputIndexFilePair(self.path, endIndex, \
                                 DummyFile(startList) if startList != [] else None, \
                                 DummyFile(endList)  if endList != [] else None)
        
        of.writeIndexes()
        of.close()
        
        self._assertIndexFile(leftContents, 'leftIndex')
        self._assertIndexFile(rightContents, 'rightIndex')
        self._removeFiles()

    def testWriteIndexes(self):
        self._assertWriteIndexes([1, 1, 1], [1, 1, 1], [-1], [], 300)
        self._assertWriteIndexes([1, 1, 1], [1, 1, 1], [-1], [0], 300)
        self._assertWriteIndexes([1, 1, 1], [1, 1, 1], [], [0], 300)
        
        self._assertWriteIndexes([0, 1, 3, 3], [1, 3, 3, 4], [10, 120, 130, 300], [], 400)
        self._assertWriteIndexes([0, 1, 2, 3], [1, 3, 3, 4], [10, 120, 130, 300], [20, 130, 300, 310], 400)
        self._assertWriteIndexes([0, 1, 2, 2], [1, 3, 4, 4], [10, 120, 130, 200], [20, 130, 350, 290], 400)
        
        self._assertWriteIndexes([0, 1, 2, 3], [3, 4, 4, 5], [], [0, 20, 130, 300, 400], 400)
        self._assertWriteIndexes([0, 1, 2, 3], [3, 4, 4, 5], [], [10, 20, 130, 300, 400], 400)
        self._assertWriteIndexes([0, 1, 1, 3], [3, 3, 3, 5], [], [10, 20, 300, 300, 400], 400)
        
        self._assertWriteIndexes([0, 1, 3, 3, 4], [1, 3, 3, 4, 4], [10, 120, 130, 300], [], 450)
        self._assertWriteIndexes([0, 1, 2, 3, 4], [1, 3, 3, 4, 4], [10, 120, 130, 300], [20, 130, 300, 310], 450)
        
        self._assertWriteIndexes([0, 1, 2, 3, 3], [3, 4, 4, 5, 5], [], [0, 20, 130, 300, 450], 450)
        self._assertWriteIndexes([0, 1, 2, 3, 3], [3, 4, 4, 5, 5], [], [10, 20, 130, 300, 450], 450)

        self._assertWriteIndexes([0, 0, 0, 2, 2, 3, 3], [0, 0, 2, 2, 3, 3, 3], [210, 220, 400], [], 650)
        self._assertWriteIndexes([0, 0, 0, 1, 2, 3, 3], [0, 0, 2, 2, 3, 3, 3], [210, 220, 400], [220, 350, 410], 650)
        
        self._assertWriteIndexes([0, 1, 1, 1, 2, 2, 2], [1, 1, 1, 2, 2, 2, 3], [0, 350, 650], [], 700)
        self._assertWriteIndexes([0, 0, 0, 0, 1, 1, 1], [1, 1, 1, 2, 2, 2, 3], [0, 350, 650], [350, 650, 700], 700)
        
        self._assertWriteIndexes([0, 0, 0, 0, 1, 1, 1], [2, 2, 2, 3, 3, 3, 4], [], [0, 350, 650, 700], 700)
        self._assertWriteIndexes([0, 0, 0, 0, 1, 1, 1], [1, 1, 2, 3, 3, 3, 4], [], [200, 350, 650, 700], 700)
    
    def runTest(self):
        self.testWriteIndexes()
    
if __name__ == "__main__":
    #TestOutputIndexFilePair().debug()
    unittest.main()
