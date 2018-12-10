import unittest
from test.gold.origdata.common.Asserts import assertBoundingRegions
from test.util.Asserts import TestCaseWithImprovedAsserts
from gold.util.CommonConstants import BINARY_MISSING_VAL
from gold.origdata.GEDependentAttributesHolder import GEDependentAttributesHolder

class TestGEDependentAttributesHolder(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass
    
    def _assertCounting(self, processedBRList, origBRTuples, origGEList):
        assertBoundingRegions(GEDependentAttributesHolder, self.assertEqual, \
                              processedBRList, origBRTuples, origGEList)
        
    def testCountElements(self):
        self._assertCounting([], \
                             [], \
                             [])
        
        self._assertCounting([['A', 'chr1', 0, 1000, 1]], \
                             [['A', 'chr1', 0, 1000, 1]], \
                             [['A', 'chr1', 10, 100]])
        
        self._assertCounting([['A', 'chr1', 0, 1000, 2], ['A', 'chr2', 0, 1000, 1]], \
                             [['A', 'chr1', 0, 1000, 2], ['A', 'chr2', 0, 1000, 1]], \
                             [['A', 'chr1', 10, 100], ['A', 'chr1', 80, 120], ['A', 'chr2', 10, 100]])
    
        self._assertCounting([['A', 'chr1', 0, 1000, 2], ['A', 'chr1', 1000, 2000, 0], ['A', 'chr2', 0, 1000, 1]], \
                             [['A', 'chr1', 0, 1000, 2], ['A', 'chr1', 1000, 2000, 0], ['A', 'chr2', 0, 1000, 1]], \
                             [['A', 'chr1', 10, 100], ['A', 'chr1', 80, 120], ['A', 'chr2', 10, 100]])
    
    def runTest(self):
        pass
        self.testCountElements()
    
if __name__ == "__main__":
    #TestGEDependentAttributesHolder().debug()
    unittest.main()
