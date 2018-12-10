import unittest
from gold.track.GenomeRegion import GenomeRegion
from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
from gold.track.SegsSampledByIntensityTrack import SegsSampledByIntensityTrack
import gold.track.SegsSampledByIntensityTrack
from gold.track.Track import PlainTrack
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from test.util.Asserts import TestCaseWithImprovedAsserts


class MyPlainTrack(object):
    _origTV = None
    
    def __init__(self, origTV):
        pass
    
    def getTrackView(self, region):
        assert region == self._origTV.genomeAnchor
        return self._origTV


class TestRandomizedSegsTrack(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass
    
    def tearDown(self):
        SegsSampledByIntensityTrack.PlainTrack = PlainTrack

    def _getInterSegLens(self, tv, binLen):
        interSegs = []
        prevEnd=0
        for el in tv:
            interSegs.append( el.start() - prevEnd )
            prevEnd = el.end()
        interSegs.append(binLen-prevEnd)
        return sorted(interSegs)

    # def _createValAndStrandDict(self, tv):
    #    mapping = {}
    #    for el in tv:
    #        mapping[len(el)] = (el.val(), el.strand())
    #
    #    return mapping
    
    def _createSortedContents(self, tv):
        return sorted([ [len(el), el.val(), el.strand(), el.id(), el.edges(), el.weights()] + [getattr(el, key)() for key in el.getAllExtraKeysInOrder()] for el in tv ])
            
    def _doRandTestSegsAndPoints(self, segments, anchor, vals=False, strands=False, ids=False, edges=False, weights=False, extras=False):
        origTV = SampleTV( starts=[x[0] for x in segments], vals=vals, strands=strands, ids=ids, edges=edges, weights=weights, extras=extras, anchor=anchor )
        self._doRandTest(origTV, [PermutedSegsAndIntersegsTrack, PermutedSegsAndSampledIntersegsTrack, SegsSampledByIntensityTrack])

        origTV = SampleTV( segments=segments, vals=vals, strands=strands, ids=ids, edges=edges, weights=weights, extras=extras, anchor=anchor )
        self._doRandTest(origTV, [PermutedSegsAndIntersegsTrack, PermutedSegsAndSampledIntersegsTrack])
        
    def _doRandTest(self, origTV, randTrackClasses):
        anchor = [origTV.genomeAnchor.start, origTV.genomeAnchor.end]
        intensityTV = SampleTV_Num(vals=range(anchor[1]-anchor[0]), anchor=anchor)  # fixme: not yet used..
        MyPlainTrack._origTV = intensityTV
        gold.track.SegsSampledByIntensityTrack.PlainTrack = MyPlainTrack
        origTrack = SampleTrack(origTV)
        anchorReg = GenomeRegion('TestGenome', 'chr21', anchor[0], anchor[1])
        binLen = len(anchorReg)
        
        for randClass in randTrackClasses:
            for i in range(100):
                randTrack = randClass(origTrack, i, trackNameIntensity='dummy_intensity')
                randTV = randTrack.getTrackView(anchorReg)
                
                self.assertListsOrDicts(sorted(len(el) for el in origTV), sorted(len(el) for el in randTV))
                
                if isinstance(randClass, PermutedSegsAndIntersegsTrack):
                    self.assertEqual(self._getInterSegLens(origTV, binLen), self._getInterSegLens(randTV, binLen))
                else:    
                    self.assertEqual(sum(self._getInterSegLens(origTV, binLen)), sum(self._getInterSegLens(randTV, binLen)))
                            
                for el in randTV:
                    assert(0 <= el.start() < el.end() <= binLen)
                
                # self.assertEqual(self._createValAndStrandDict(origTV), self._createValAndStrandDict(randTV))
                self.assertListsOrDicts(self._createSortedContents(origTV), self._createSortedContents(randTV))

    def testRandomization(self):
        self._doRandTestSegsAndPoints( segments=[], anchor=[100,400])
        self._doRandTestSegsAndPoints( segments=[[0,300]], anchor=[100,400])
        self._doRandTestSegsAndPoints( segments=[[10,30]], vals=True, strands=True, anchor=[100,400])
    
        self._doRandTestSegsAndPoints( segments=[[10,30],[60,100],[150,210]], vals=False, strands=False, ids=False, edges=False, weights=False, extras=False, anchor=[100,400])
        self._doRandTestSegsAndPoints( segments=[[10,30],[60,100],[150,210]], vals=True, strands=True, ids=True, edges=True, weights=True, extras=True, anchor=[100,400])

    def runTest(self):
        pass


if __name__ == "__main__":
    # TestPermutedSegsAndIntersegsRandomizedTrack().debug()
    unittest.main()
