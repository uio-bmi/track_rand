#!/usr/bin/env python
import ast
import unittest
import os
import sys
from collections import OrderedDict
from copy import deepcopy

from gold.util.CommonFunctions import createDirPath
from gold.origdata.GenomeElementSource import BoundingRegionTuple
from gold.track.GenomeRegion import GenomeRegion
from quick.util.GenomeInfo import GenomeInfo
from gold.track.Track import Track
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import AutonomousTrackElement
from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
from test.gold.origdata.common.TestWithGeSourceData import TestWithGeSourceData
from test.integration.ProfiledIntegrationTest import ProfiledIntegrationTest

PreProcessAllTracksJob.PASS_ON_EXCEPTIONS = True

class TestTrackPreProcessor(ProfiledIntegrationTest, TestWithGeSourceData):
    GENOME = 'TestGenome'

    def _preProcess(self, trackName, noOverlapsFileCount=None, withOverlapsFileCount=None, \
                    noOverlapsChrElCount=None, withOverlapsChrElCount=None, customBins={}):
        trackName = self.TRACK_NAME_PREFIX + trackName
        noOverlapsPath = createDirPath(trackName, self.GENOME, allowOverlaps=False)
        withOverlapsPath = createDirPath(trackName, self.GENOME, allowOverlaps=True)
        self._removeDir(noOverlapsPath, trackName)
        self._removeDir(withOverlapsPath, trackName)

        self._runWithProfiling('PreProcessAllTracksJob(' + repr(self.GENOME) + ',' +
                               repr(trackName) + ', username="Test").process()',
                               {'PreProcessAllTracksJob', PreProcessAllTracksJob})

        if noOverlapsFileCount is not None:
            self.assertEquals(noOverlapsFileCount, len([x for x in os.listdir(noOverlapsPath) if not x.startswith('.')]))

        if withOverlapsFileCount is not None:
            self.assertEquals(withOverlapsFileCount, len([x for x in os.listdir(withOverlapsPath) if not x.startswith('.')]))

        if noOverlapsChrElCount is not None:
            self.assertChrElCounts(trackName, noOverlapsChrElCount, False, customBins)

        if withOverlapsChrElCount is not None:
            self.assertChrElCounts(trackName, withOverlapsChrElCount, True, customBins)

        self._storeProfile()

    def assertChrElCounts(self, trackName, chrElCountDict, allowOverlaps, customBins):
        for chr in chrElCountDict.keys():
            if chr in customBins:
                region = customBins[chr]
            else:
                region = GenomeRegion(self.GENOME, chr, 0, GenomeInfo.getChrLen(self.GENOME, chr))
            tv = self._getTrackView(trackName, region, allowOverlaps)
            self.assertEquals(chrElCountDict[chr], len([x for x in tv]))

    def _getTrackView(self, trackName, region, allowOverlaps):
        track = Track(trackName)
        track.addFormatReq(TrackFormatReq(allowOverlaps=allowOverlaps))
        return track.getTrackView(region)

    def _getBoundingRegionTupleList(self, case, sortedAssertElList):
        boundingRegions = [br for br in sorted(case.boundingRegionsAssertList) if br.region.chr is not None]
        if len(boundingRegions) > 0:
            return [BoundingRegionTuple(GenomeRegion(self.GENOME, chr=br.region.chr, \
                                                     start=br.region.start if br.region.start is not None else 0, \
                                                     end=br.region.end if br.region.end is not None else \
                                                         GenomeInfo.getChrLen(self.GENOME, br.region.chr)), br.elCount)
                    for br in boundingRegions]
        else:
            totChrList = [ge.chr for ge in sortedAssertElList]
            chrBrList = OrderedDict( [ (i, totChrList.count(i)) for i in sorted(set(totChrList)) ] )
            return [BoundingRegionTuple(GenomeRegion(self.GENOME, chr=chr, start=0, \
                                                     end=GenomeInfo.getChrLen(self.GENOME, chr)), elCount) \
                    for chr, elCount in chrBrList.iteritems()]

    def _getCaseTrackView(self, case, br, allowOverlaps):
        return self._getTrackView(self.TRACK_NAME_PREFIX + case.trackName, \
                                  GenomeRegion(genome=self.GENOME, chr=br.chr, start=br.start, end=br.end), \
                                  allowOverlaps=allowOverlaps)

    def _assertGenomeAndTrackElementEqual(self, ge, te, teChr, teOffset):
        self.assertEqual(ge.chr, teChr)

        if ge.start is not None:
            self.assertEqual(ge.start, te.start() + teOffset)
        if ge.end is not None:
            self.assertEqual(ge.end, te.end() + teOffset)
        if ge.edges is not None:
            self.assertListsOrDicts(ge.edges, te.edges()[te.edges()!=''])
        if ge.weights is not None:
            self.assertListsOrDicts(ge.weights, te.weights()[te.edges()!=''])

        for attr in ['val', 'strand', 'id']:
            self.assertListsOrDicts(getattr(ge, attr), getattr(te, attr)())
        for attr in ge.orderedExtraKeys:
            self.assertListsOrDicts(ge.extra[attr], getattr(te, attr)())

    def _testTrackReading(self, case, allowOverlaps):
        allAssertEls = []
        allTrackEls = []
        trackElChrs = []
        trackElOffsets = []
        prevAssertElCount = 0

        sortedAssertElList = sorted(case.assertElementList, key=lambda el:[el.chr, el.start, el.end])

        if case.targetClass._isSliceSource:
            expandedAssertElList = []
            for assertEl in sortedAssertElList:
                for prefix in case.prefixList:
                    contents = getattr(assertEl, prefix)
                    for i in range(len(contents)):
                        el = deepcopy(assertEl)
                        setattr(el, prefix, contents[i])
                        expandedAssertElList.append(el)
            sortedAssertElList = expandedAssertElList

        for brTuple in self._getBoundingRegionTupleList(case, sortedAssertElList):
            if 'end' in case.prefixList and not 'start' in case.prefixList: #GP, SF, LGP, LSF
                assertElStartIdx = prevAssertElCount + 1
            else:
                assertElStartIdx = prevAssertElCount
            assertElEndIdx = prevAssertElCount + brTuple.elCount
            assertEls = sortedAssertElList[assertElStartIdx:assertElEndIdx]

            tv = self._getCaseTrackView(case, brTuple.region, allowOverlaps)
            self.assertEqual(len(assertEls), tv.getNumElements())

            allAssertEls += assertEls
            allTrackEls += [AutonomousTrackElement(trackEl=x) for x in tv]
            trackElChrs += [brTuple.region.chr for x in tv]
            trackElOffsets += [tv.genomeAnchor.start for x in tv]
            prevAssertElCount += brTuple.elCount

        for i,ge in enumerate(allAssertEls):
            self._assertGenomeAndTrackElementEqual(ge, allTrackEls[i], trackElChrs[i], trackElOffsets[i])

class TestGESourceTestsPreprocessing(TestTrackPreProcessor):
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']

    def testAll(self):
        testGESource = self._commonSetup()

        for caseName in testGESource.cases:
            print caseName
            case = testGESource.cases[caseName]
            if caseName.endswith('_no_hb'):
                print 'Test case skipped...'
                continue

            self._writeTestFile(case)
            self._preProcess(case.trackName)

            allowOverlaps = True if ('start' in case.prefixList) and '_no_overlaps' not in caseName else False
            self._testTrackReading(case, allowOverlaps=allowOverlaps)

        self._removeAllTrackData(self.TRACK_NAME_PREFIX)

    def testAllExceptions(self):
        testGESource = self._commonSetup()

        for caseName in testGESource.exceptionCases:
            print caseName
            case = testGESource.exceptionCases[caseName]
            if caseName.endswith('_no_hb'):
                print 'Test case skipped...'
                continue

            self._writeTestFile(case)
            self.assertRaises(case.exceptionClass, self._preProcess, case.trackName)

        self._removeAllTrackData(self.TRACK_NAME_PREFIX)

class TestGESourceTracksPreprocessing(TestTrackPreProcessor):
    TRACK_NAME_PREFIX = ['GESourceTracks']

    def testPreProcessBed(self):
        self._preProcess(['BedGenomeElementSource'], \
        noOverlapsFileCount=14, \
        withOverlapsFileCount=14, \
        noOverlapsChrElCount={'chr21':242, 'chrM':11}, \
        withOverlapsChrElCount={'chr21':828, 'chrM':11})

    def testPreProcessBedPoint(self):
        self._preProcess(['PointBedGenomeElementSource'], \
        noOverlapsFileCount=7, \
        withOverlapsFileCount=7, \
        noOverlapsChrElCount={'chr21':139, 'chrM':8}, \
        withOverlapsChrElCount={'chr21':139, 'chrM':8})

    def testPreProcessBedCategory(self):
        self._preProcess(['BedCategoryGenomeElementSource'], \
        noOverlapsFileCount=6, \
        withOverlapsFileCount=6, \
        noOverlapsChrElCount={'chr21':38, 'chrM':0}, \
        withOverlapsChrElCount={'chr21':87, 'chrM':0})

    def testPreProcessBedValued(self):
        self._preProcess(['BedValuedGenomeElementSource'], \
        noOverlapsFileCount=8, \
        withOverlapsFileCount=8, \
        noOverlapsChrElCount={'chr21':38, 'chrM':0}, \
        withOverlapsChrElCount={'chr21':87, 'chrM':0})

    def testPreProcessFasta(self):
        self._preProcess(['FastaGenomeElementSource'], \
        noOverlapsFileCount=2, \
        withOverlapsFileCount=None, \
        noOverlapsChrElCount={'chr21':9804, 'chrM':0}, \
        withOverlapsChrElCount=None, \
        customBins={'chr21':GenomeRegion(self.GENOME, 'chr21', 0, 9804)})

    def testPreProcessGff(self):
        self._preProcess(['GffGenomeElementSource'], \
        noOverlapsFileCount=12, \
        withOverlapsFileCount=12, \
        noOverlapsChrElCount={'chr21':3076, 'chrM':0}, \
        withOverlapsChrElCount={'chr21':5260, 'chrM':0})

    def testPreProcessMicroarray(self):
        self._preProcess(['MicroarrayGenomeElementSource'], \
        noOverlapsFileCount=7, \
        withOverlapsFileCount=7, \
        noOverlapsChrElCount={'chr21':2, 'chrM':0}, \
        withOverlapsChrElCount={'chr21':2, 'chrM':0})

    def testPreProcessBedGraph(self):
        self._preProcess(['BedGraphGenomeElementSource'], \
        noOverlapsFileCount=6, \
        withOverlapsFileCount=6, \
        noOverlapsChrElCount={'chr21':10000, 'chrM':0}, \
        withOverlapsChrElCount={'chr21':10000, 'chrM':0})

    def testPreProcessBedGraphTargetControl(self):
        self._preProcess(['BedGraphTargetControlGenomeElementSource'], \
        noOverlapsFileCount=6, \
        withOverlapsFileCount=6, \
        noOverlapsChrElCount={'chr21':2, 'chrM':1}, \
        withOverlapsChrElCount={'chr21':2, 'chrM':1})

    def testPreProcessHBFunction(self):
        self._preProcess(['HBFunctionGenomeElementSource'], \
        noOverlapsFileCount=2, \
        withOverlapsFileCount=None, \
        noOverlapsChrElCount=None, \
        withOverlapsChrElCount=None)

    def testPreProcessPoisitionIter(self):
        self._preProcess(['PositionIterGESource'], \
        noOverlapsFileCount=4, \
        withOverlapsFileCount=None, \
        noOverlapsChrElCount={'chr21':139, 'chrM':8}, \
        withOverlapsChrElCount=None)

    def runTest(self):
        pass
        #self.testPreProcessMicroarray()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        TestTrackPreProcessor.VERBOSE = ast.literal_eval(sys.argv[1])
        sys.argv = sys.argv[:-1]
    #TestTrackPreProcessor().run()
    #TestTrackPreProcessor().debug()
    unittest.main()
