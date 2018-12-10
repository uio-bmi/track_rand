import unittest
from test.util.Asserts import TestCaseWithImprovedAsserts, AssertList

from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackSource import TrackData
from test.gold.track.common.SampleTrackView import getRandValList, getRandStrandList, getRandGraphLists
#import gold.track.TrackViewLoader
import gold.util.CompBinManager

class TestTrackViewLoader(TestCaseWithImprovedAsserts):
    def setUp(self):
        self.prevCompBinSize = gold.util.CompBinManager.COMP_BIN_SIZE
        gold.util.CompBinManager.COMP_BIN_SIZE = 100
        #self.prevCompBinSize = gold.track.TrackViewLoader.COMP_BIN_SIZE
        #gold.track.TrackViewLoader.COMP_BIN_SIZE = 100
        from gold.track.TrackViewLoader import TrackViewLoader 
        self.trackViewLoader = TrackViewLoader()

    def tearDown(self):
        gold.util.CompBinManager.COMP_BIN_SIZE = self.prevCompBinSize
        #gold.track.TrackViewLoader.COMP_BIN_SIZE = self.prevCompBinSize        

    def _assertTrackViewLoading_Numbers(self, trackData, start, end):
        trackView = self.trackViewLoader.loadTrackView(trackData, GenomeRegion(genome='TestGenome', start=start, end=end), 'crop', False)
        self.assertListsOrDicts(trackData['val'][start:end], [el.val() for el in trackView])
        self.assertListsOrDicts(trackData['strand'][start:end], [el.strand() for el in trackView])
        self.assertListsOrDicts(trackData['id'][start:end], [el.id() for el in trackView])
        self.assertListsOrDicts(trackData['edges'][start:end], [el.edges() for el in trackView])
        self.assertListsOrDicts(trackData['weights'][start:end], [el.weights() for el in trackView])
        self.assertListsOrDicts(trackData['a'][start:end], [el.a() for el in trackView])
        self.assertListsOrDicts(trackData['b'][start:end], [el.b() for el in trackView])
        
    def _getTrackData_Numbers(self, size):
        id, edges, weights = getRandGraphLists(size, maxNumEdges=10)
        return TrackData({'val': list(getRandValList(size)), \
                          'strand': list(getRandStrandList(size)), \
                          'id': list(id), \
                          'edges': list(edges), \
                          'weights': list(weights), \
                          'a': [str(x) for x in xrange(size)], \
                          'b': [str(x) for x in xrange(size, 0, -1)]})
    
    def testLoadTrackView_Numbers(self):
        trackData = self._getTrackData_Numbers(900)
        self._assertTrackViewLoading_Numbers(trackData, 0, 100)
        self._assertTrackViewLoading_Numbers(trackData, 0, 900)
        self._assertTrackViewLoading_Numbers(trackData, 300, 700)

        self._assertTrackViewLoading_Numbers(trackData, 312, 700)
        self._assertTrackViewLoading_Numbers(trackData, 300, 687)
        self._assertTrackViewLoading_Numbers(trackData, 312, 687)
        
        self._assertTrackViewLoading_Numbers(trackData, 0, 0)
        self._assertTrackViewLoading_Numbers(trackData, 300, 300)
        self._assertTrackViewLoading_Numbers(trackData, 400, 300)
        
        trackData = self._getTrackData_Numbers(891)
        self._assertTrackViewLoading_Numbers(trackData, 800, 880)
        self._assertTrackViewLoading_Numbers(trackData, 800, 891)
        self._assertTrackViewLoading_Numbers(trackData, 700, 880)
        
    def _assertTrackViewLoading_Segments(self, trackData, indexList, start, end):
        trackView = self.trackViewLoader.loadTrackView(trackData, GenomeRegion(genome='TestGenome', start=start, end=end),'crop',False)
        i = -1
        for i,el in enumerate(trackView):
            if i < len(indexList):
                index = indexList[i]
            else:
                self.fail()
            self.assertEqual(max(0, trackData['start'][index] - start), el.start())
            self.assertEqual(min(end, trackData['end'][index]) - start, el.end())
            self.assertAlmostEqual(trackData['val'][index], el.val())
            self.assertEqual(trackData['strand'][index], el.strand())
            self.assertEqual(trackData['id'][index], el.id())
            self.assertListsOrDicts(trackData['edges'][index], el.edges())
            self.assertListsOrDicts(trackData['weights'][index], el.weights())
            self.assertEqual(trackData['a'][index], el.a())
            self.assertEqual(trackData['b'][index], el.b())
            self.assertRaises(AttributeError, lambda: el.leftIndex)
            self.assertRaises(AttributeError, lambda: el.rightIndex)
        self.assertEqual(len(indexList), i+1)
    
    def testLoadTrackView_Segments(self):
        id, edges, weights = getRandGraphLists(4)
        trackData = TrackData({'start' : [10, 210, 260, 410],\
                               'end' : [20, 240, 310, 710],\
                               'val' : list(getRandValList(4)),\
                               'strand' : list(getRandStrandList(4)),\
                               'id': list(id), \
                               'edges': list(edges), \
                               'weights': list(weights), \
                               'a': ['A', 'B', 'C', 'D'], \
                               'b': ['1.0', '2.0', '3.0', '4.0'], \
                               'leftIndex' : [0, 1, 1, 1, 3, 3, 3, 3, 4],\
                               'rightIndex' : [1, 1, 3, 3, 4, 4, 4, 4, 4]})
        
        self._assertTrackViewLoading_Segments(trackData, [0], 0, 100)
        self._assertTrackViewLoading_Segments(trackData, [1, 2], 200, 300)
        self._assertTrackViewLoading_Segments(trackData, [0, 1, 2, 3], 0, 900)
        self._assertTrackViewLoading_Segments(trackData, [2, 3], 300, 700)

        self._assertTrackViewLoading_Segments(trackData, [3], 310, 700)
        self._assertTrackViewLoading_Segments(trackData, [2], 300, 410)
        self._assertTrackViewLoading_Segments(trackData, [], 310, 410)

        self._assertTrackViewLoading_Segments(trackData, [], 0, 0)
        self._assertTrackViewLoading_Segments(trackData, [], 300, 300)
        self._assertTrackViewLoading_Segments(trackData, [], 400, 400)
        
    def runTest(self):
        self.testLoadTrackView_Numbers()
    
if __name__ == "__main__":
    #TestTrackViewLoader().debug()
    unittest.main()
