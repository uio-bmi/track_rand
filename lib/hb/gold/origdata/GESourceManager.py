from gold.origdata.GESourceWrapper import BrTuplesGESourceWrapper
from gold.origdata.GEOverlapClusterer import GEOverlapClusterer
from gold.origdata.GEBoundingRegionElementCounter import GEBoundingRegionElementCounter
from gold.origdata.GenomeElementSource import BoundingRegionTuple
from gold.origdata.GEDependentAttributesHolder import GEDependentAttributesHolder
from gold.origdata.TrackGenomeElementSource import TrackGenomeElementSource
from gold.util.CommonFunctions import flatten
from gold.util.CommonConstants import RESERVED_PREFIXES
from gold.util.CommonClasses import OrderedDefaultDict
from gold.util.CustomExceptions import NotSupportedError
from gold.track.TrackFormat import TrackFormat
from collections import defaultdict
from functools import partial

class GESourceManager(object):
    def __init__(self, geSource):
        self._geSource = self._decorateGESource(geSource)
        self._boundingRegionsAndGEsCorrespond = None

        self._areValsCategorical = TrackFormat.createInstanceFromGeSource(geSource).getValTypeName() == 'Category'
        self._areEdgeWeightsCategorical = TrackFormat.createInstanceFromGeSource(geSource).getWeightTypeName() == 'Category'
        self._valCategories = set()
        self._edgeWeightCategories = set()

        self._numElements = OrderedDefaultDict(int)
        self._maxStrLens = OrderedDefaultDict(partial(self._initMaxStrLens, self._getMaxStrLensKeys()))
        self._maxNumEdges = OrderedDefaultDict(int)

        self._hasCalculatedStats = False
#        self._calcStatisticsInExtraPass()

    def _decorateGESource(self, geSource):
        return GEDependentAttributesHolder(geSource)

    def _getMaxStrLensKeys(self):
        prefixSet = set(self._geSource.getPrefixList())

        return (['val'] if 'val' in prefixSet and self._geSource.getValDataType() == 'S' else []) + \
               (['id'] if 'id' in prefixSet else []) + \
               (['edges'] if 'edges' in prefixSet else []) + \
               (['weights'] if 'weights' in prefixSet and self._geSource.getEdgeWeightDataType() == 'S' else []) + \
               [x for x in prefixSet if x not in RESERVED_PREFIXES]

    @staticmethod
    def _initMaxStrLens(keys):
        return dict([(x,0) for x in keys])

    def _calcStatisticsInExtraPass(self):
        if not self._hasCalculatedStats:
            prevPrintWarnings = self._geSource.getPrintWarnings()
            self._geSource.setPrintWarnings(False)

            if self._geSource.isSliceSource():
                if len(self._getMaxStrLensKeys()):
                    raise NotImplementedError('Dimension calculation not yet implemented for slice-based GenomeElementSources.')

                prefixList = self._geSource.getPrefixList()
                for el in self._geSource:
                    chr = el.chr
                    self._numElements[chr] += len(getattr(el, prefixList[0]))
            else:
                for el in self._geSource:
                    chr = el.chr
                    self._numElements[chr] += 1

                    if el.isBlankElement:
                        continue

                    if self._areValsCategorical:
                        self._valCategories.add(el.val)

                    if self._areEdgeWeightsCategorical:
                        self._edgeWeightCategories |= set(el.weights)

                    for prefix in self._maxStrLens[chr]:
                        content = getattr(el, prefix, None)

                        if content is not None:
                            self._maxStrLens[chr][prefix] = \
                                    max( self._maxStrLens[chr][prefix], \
                                         max(1, len(content)) if isinstance(content, basestring) else \
                                            max([1] + [len(x) for x in flatten(content)]) )

                            if prefix == 'edges':
                                self._maxNumEdges[chr] = max(self._maxNumEdges[chr], len(el.edges))

            self._geSource.setPrintWarnings(prevPrintWarnings)
            self._hasCalculatedStats = True

    def getGESource(self):
        return self._geSource

    def getBoundingRegionTuples(self):
        boundingRegionTuples = [x for x in self._getBoundingRegionTuples() \
                                if x.region.chr is not None]

        if len(boundingRegionTuples) == 0:
            from gold.origdata.GenomeElementSource import BoundingRegionTuple
            from gold.track.GenomeRegion import GenomeRegion
            from quick.util.GenomeInfo import GenomeInfo

            geChrList = self.getAllChrs()
            boundingRegionTuples = [BoundingRegionTuple( \
                                     GenomeRegion(chr=chr, start=0, end=GenomeInfo.getChrLen(self._geSource.genome, chr)), \
                                     self.getNumElementsForChr(chr) ) \
                                    for chr in geChrList]
            self._boundingRegionsAndGEsCorrespond = False
        else:
            self._boundingRegionsAndGEsCorrespond = True

        return boundingRegionTuples

    def _getBoundingRegionTuples(self):
        return self._geSource.getBoundingRegionTuples()

    def boundingRegionsAndGEsCorrespond(self):
        assert self._boundingRegionsAndGEsCorrespond is not None
        return self._boundingRegionsAndGEsCorrespond

    def getPrefixList(self):
        return self._geSource.getPrefixList()

    def getValDataType(self):
        return self._geSource.getValDataType()

    def getValDim(self):
        return self._geSource.getValDim()

    def getEdgeWeightDataType(self):
        return self._geSource.getEdgeWeightDataType()

    def getEdgeWeightDim(self):
        return self._geSource.getEdgeWeightDim()

    def isSorted(self):
        return self._geSource.isSorted()

    def getAllChrs(self):
        self._calcStatisticsInExtraPass()
        return self._numElements.keys()

    def getNumElements(self):
        self._calcStatisticsInExtraPass()
        return sum(self._numElements.values())

    def getNumElementsForChr(self, chr):
        self._calcStatisticsInExtraPass()
        return self._numElements[chr]

    def getValCategories(self):
        self._calcStatisticsInExtraPass()
        return self._valCategories

    def getEdgeWeightCategories(self):
        self._calcStatisticsInExtraPass()
        return self._edgeWeightCategories

    def getMaxNumEdges(self):
        self._calcStatisticsInExtraPass()
        return max(self._maxNumEdges.values())

    def getMaxNumEdgesForChr(self, chr):
        self._calcStatisticsInExtraPass()
        return self._maxNumEdges[chr]

    def getMaxStrLens(self):
        self._calcStatisticsInExtraPass()
        return reduce(lambda x,y:dict((key, max(x[key], y[key])) for key in x.keys()), \
               self._maxStrLens.values())

    def getMaxStrLensForChr(self, chr):
        self._calcStatisticsInExtraPass()
        return self._maxStrLens[chr]

    def getMaxChrStrLen(self):
        self._calcStatisticsInExtraPass()
        return max(len(chr) for chr in self._maxStrLens.keys())


class OverlapClusteringGESourceManager(GESourceManager):
    def __init__(self, genome, trackName, origBrTuples):
        self._origBrTuples = origBrTuples
        trackGESource = TrackGenomeElementSource(genome, trackName, \
                                                 [br.region for br in self._origBrTuples],
                                                 allowOverlaps=True)

        GESourceManager.__init__(self, trackGESource)
        self._brTuplesForClusteredElements = None

    def _decorateGESource(self, geSource):
        return GEBoundingRegionElementCounter(GEOverlapClusterer(geSource), \
                                              self._origBrTuples)


class RegionBasedGESourceManager(GESourceManager):
    def __init__(self, geSource, brRegionList, calcStatsInExtraPass, countElsInBoundingRegions):
        assert len(brRegionList) > 0
        self._brRegionList = brRegionList
        self._calcStatsInExtraPass = calcStatsInExtraPass
        self._countElsInBoundingRegions = countElsInBoundingRegions
        GESourceManager.__init__(self, geSource)

    def _decorateGESource(self, geSource):
        if self._countElsInBoundingRegions:
            brTuples = [BoundingRegionTuple(region, 0) for region in self._brRegionList]
            return GEBoundingRegionElementCounter(geSource, brTuples)
        else:
            brTuples = [BoundingRegionTuple(region, len(region)) for region in self._brRegionList]
            return BrTuplesGESourceWrapper(geSource, brTuples)

    def _calcStatisticsInExtraPass(self):
        if not self._hasCalculatedStats:
            if self._calcStatsInExtraPass:
                GESourceManager._calcStatisticsInExtraPass(self)
            else:
                for br in self._brRegionList:
                    self._numElements[br.chr] += len(br)
                self._hasCalculatedStats = True
