import unittest
from tempfile import NamedTemporaryFile

from gold.origdata.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
from gold.origdata.BedComposer import BedComposer, PointBedComposer, CategoryBedComposer, ValuedBedComposer
from gold.origdata.BedGraphComposer import BedGraphComposer
from gold.origdata.WigComposer import WigComposer
from gold.origdata.GffComposer import GffComposer, CategoryGffComposer
from gold.origdata.FastaComposer import FastaComposer
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GEDependentAttributesHolder import GEDependentAttributesHolder
from gold.origdata.TrackGenomeElementSource import TrackGenomeElementSource
from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
from gold.util.CommonFunctions import createDirPath
from quick.application.UserBinSource import GlobalBinSource
from test.gold.origdata.common.TestWithGeSourceData import TestWithGeSourceData
from test.util.Asserts import TestCaseWithImprovedAsserts

PreProcessAllTracksJob.PASS_ON_EXCEPTIONS = True

class TestFileFormatComposers(TestWithGeSourceData, TestCaseWithImprovedAsserts):
    GENOME = 'TestGenome'
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']

    def setUp(self):
        pass

    def _preProcess(self, trackName):
        self._removeDir(createDirPath(trackName, self.GENOME, allowOverlaps=False), trackName)
        self._removeDir(createDirPath(trackName, self.GENOME, allowOverlaps=True), trackName)
        PreProcessAllTracksJob(self.GENOME, trackName, username="Test").process()

    def testGtrackComposer(self):
        self._commonTestGtrackComposer(withTrackGESource=False)

    def testGtrackFromTrackComposer(self):
        self._commonTestGtrackComposer(withTrackGESource=True)

    def _commonTestGtrackComposer(self, withTrackGESource):
        for useExtendedGtrack in [False, True]:
            print 'Using ' + ('extended' if useExtendedGtrack else 'standard') + ' GTrack specification'
            composerCls = ExtendedGtrackComposer if useExtendedGtrack else StdGtrackComposer
            self._commonTestComposer(withTrackGESource, composerCls, suffix='gtrack')

    def testBedComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=BedComposer, suffix='bed')

    def testBedFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=BedComposer, suffix='bed')

    def testPointBedComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=PointBedComposer, suffix='point.bed')

    def testPointBedFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=PointBedComposer, suffix='point.bed')

    def testCategoryBedComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=CategoryBedComposer, suffix='category.bed')

    def testCategoryBedFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=CategoryBedComposer, suffix='category.bed')

    def testValuedBedComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=ValuedBedComposer, suffix='valued.bed')

    def testMarkedBedFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=ValuedBedComposer, suffix='valued.bed')

    def testBedGraphComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=BedGraphComposer, suffix='bedgraph')

    def testBedGraphFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=BedGraphComposer, suffix='bedgraph')

    def testWigComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=WigComposer, suffix='wig')

    def testWigFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=WigComposer, suffix='wig')

    def testGffComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=GffComposer, suffix='gff')

    def testGffFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=GffComposer, suffix='gff')

    def testCategoryGffComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=CategoryGffComposer, suffix='category.gff')

    def testCategoryGffFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=CategoryGffComposer, suffix='category.gff')

    def testFastaComposer(self):
        self._commonTestComposer(withTrackGESource=False, composerCls=FastaComposer, suffix='fasta')

    def testFastaFromTrackComposer(self):
        self._commonTestComposer(withTrackGESource=True, composerCls=FastaComposer, suffix='fasta')

    def _commonTestComposer(self, withTrackGESource, composerCls, suffix):
        geSourceTest = self._commonSetup()

        for caseName in geSourceTest.cases:
            if not (caseName == suffix or \
                    (caseName.startswith(suffix) and caseName[len(suffix)] in ['_','.'])):
                continue

            if 'no_print' in caseName or \
                withTrackGESource and ('no_track_extract' in caseName or \
                                       caseName.endswith('_no_hb')):
                print 'Test case skipped: ' + caseName
                continue

            print caseName
            case = geSourceTest.cases[caseName]

            testFn = self._writeTestFile(case)
            sourceClass = case.sourceClass if case.sourceClass is not None else GenomeElementSource
            genome = self.GENOME if withTrackGESource else case.genome

            rawCaseGESource = sourceClass(testFn, genome, printWarnings=False)
            caseGESource = GEDependentAttributesHolder(rawCaseGESource)
            #actualSourceClass = caseGESource._geSource.__class__

            if withTrackGESource:
                for x in caseGESource:
                    pass

                boundingRegionTuples = caseGESource.getBoundingRegionTuples()
                boundingRegions = [br.region for br in boundingRegionTuples]
                if boundingRegions == [] or all(br.chr is None for br in boundingRegions):
                    boundingRegions = GlobalBinSource(self.GENOME)

                trackName = self.TRACK_NAME_PREFIX + case.trackName
                self._preProcess(trackName)

                allowOverlaps = True if ('start' in case.prefixList) and not caseName.endswith('_compose_no_overlaps') else False
                inputGESource = TrackGenomeElementSource(self.GENOME, trackName, boundingRegions, \
                                                         printWarnings=False, allowOverlaps=allowOverlaps)
            else:
                inputGESource = rawCaseGESource

            composer = composerCls(inputGESource)
            contents = composer.returnComposed()
            print contents

            composedFile = NamedTemporaryFile('w', suffix='.' + suffix)
            composedFile.write(contents)
            composedFile.flush()

            #print actualSourceClass.__name__

            outputGESource = GEDependentAttributesHolder(sourceClass(composedFile.name, genome, printWarnings=False))

            if 'no_check_print' in caseName or withTrackGESource and 'no_check_track_extract' in caseName:
                print 'No checks for case: ' + caseName
            else:
                caseGEs = [ge.getCopy() for ge in caseGESource]
                outputGEs = [ge.getCopy() for ge in outputGESource]
                isSortableGE = any(getattr(caseGEs[0], x) is not None for x in ['start','end']) if len(caseGEs) > 0 else False
                if withTrackGESource and isSortableGE and not caseGESource.hasBoundingRegionTuples():
                    caseGEs = sorted(caseGEs)
                self.assertGenomeElementLists(caseGEs, outputGEs)
                self.assertListsOrDicts(caseGESource.getBoundingRegionTuples(), outputGESource.getBoundingRegionTuples())

            if withTrackGESource:
                self._removeAllTrackData(self.TRACK_NAME_PREFIX)

    def runTest(self):
        pass

if __name__ == "__main__":
    #TestFileFormatComposers().debug()
    unittest.main()
