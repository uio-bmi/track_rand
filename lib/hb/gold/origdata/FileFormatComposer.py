from collections import namedtuple
from cStringIO import StringIO
from config.Config import OUTPUT_PRECISION
from gold.util.CustomExceptions import InvalidFormatError, AbstractClassError, NotIteratedYetError
from quick.util.CommonFunctions import isNan, ensurePathExists
from gold.util.CommonConstants import BINARY_MISSING_VAL
from gold.origdata.GEDependentAttributesHolder import GEDependentAttributesHolder

MatchResult = namedtuple('MatchResult', ['match', 'trackFormatName'])
ComposerInfo = namedtuple('ComposerInfo', ['trackFormatName','fileFormatName','fileSuffix'])


def findMatchingFileFormatComposers(trackFormat):
    matchingComposers = []
    for composer in getAllComposers():
        matchResult = composer.matchesTrackFormat(trackFormat)
        if matchResult.match:
            matchingComposers.append(ComposerInfo(trackFormatName=matchResult.trackFormatName, \
                                                  fileFormatName=composer.FILE_FORMAT_NAME, \
                                                  fileSuffix=composer.getDefaultFileNameSuffix()))
    return matchingComposers


def getComposerClsFromFileFormatName(fileFormatName):
    for composerCls in getAllComposers():
        if fileFormatName.lower() == composerCls.FILE_FORMAT_NAME.lower():
            return composerCls
    raise InvalidFormatError("Error: file format composer for format '%s' was not found." % fileFormatName)


def getComposerClsFromFileSuffix(fileSuffix):
    for composerCls in getAllComposers():
        if fileSuffix.lower() in [x.lower() for x in composerCls.FILE_SUFFIXES]:
            return composerCls
    raise InvalidFormatError("Error: file format composer for file suffix '%s' was not found." % fileSuffix)


class FileFormatComposer(object):
    FILE_SUFFIXES = ['']
    FILE_FORMAT_NAME = ''

    def __init__(self, geSource):
        try:
            if not geSource.hasBoundingRegionTuples():
                self._geSource = GEDependentAttributesHolder(geSource)
            else:
                self._geSource = geSource
        except NotIteratedYetError:
            self._geSource = geSource

        try:
            self._geSource.parseFirstDataLine()
            self._emptyGeSource = False
        except:
            self._emptyGeSource = True

        #self._emptyGeSource = True
        #for ge in self._geSource:
        #    self._emptyGeSource = False
        #    break

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=False, trackFormatName=trackFormat.getFormatName())

    def composeToFile(self, fn, ignoreEmpty=False, **kwArgs):
        ensurePathExists(fn)
        f = open(fn, 'w')
        ok = self._composeCommon(f, ignoreEmpty, **kwArgs)
        f.close()
        return ok

    def returnComposed(self, ignoreEmpty=False, **kwArgs):
        memFile = StringIO()
        self._composeCommon(memFile, ignoreEmpty, **kwArgs)
        return memFile.getvalue()

    def _composeCommon(self, out, ignoreEmpty=False, **kwArgs):
        if ignoreEmpty and self._emptyGeSource:
            return False

        self._compose(out, **kwArgs)
        return True

    def _compose(self, out, **kwArgs):
        raise AbstractClassError()

    def _commonFormatNumberVal(self, val):
        if isNan(val) or val is None:
            return '.'
        return ('%#.' + str(OUTPUT_PRECISION) + 'g') % val
        #return '%.5f' % val

    def _commonFormatBinaryVal(self, val):
        if val == BINARY_MISSING_VAL:
            return '.'
        return 1 if val == True else 0

    @classmethod
    def getDefaultFileNameSuffix(cls):
        return cls.FILE_SUFFIXES[0]


def getAllComposers():
    from gold.origdata.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
    from gold.origdata.BedComposer import BedComposer, PointBedComposer, CategoryBedComposer, ValuedBedComposer
    from gold.origdata.BedGraphComposer import BedGraphComposer, BedGraphTargetControlComposer
    from gold.origdata.GffComposer import GffComposer, CategoryGffComposer
    from gold.origdata.WigComposer import WigComposer
    from gold.origdata.FastaComposer import FastaComposer

    return [BedComposer, PointBedComposer, CategoryBedComposer, ValuedBedComposer, BedGraphComposer, \
            BedGraphTargetControlComposer, GffComposer, CategoryGffComposer, WigComposer, FastaComposer, \
            StdGtrackComposer, ExtendedGtrackComposer]
