import copy
import numpy
from collections import OrderedDict
from gold.application.LogSetup import logMessage
from gold.track.SmartMemmap import SmartMemmap
from gold.util.CommonConstants import RESERVED_PREFIXES
from gold.util.CustomExceptions import ShouldNotOccurError, NotSupportedError

# Track type constants

POINTS = 'points'
VALUED_POINTS = 'valued points'
SEGMENTS = 'segments'
VALUED_SEGMENTS = 'valued segments'
GENOME_PARTITION = 'genome partition'
STEP_FUNCTION = 'step function'
FUNCTION = 'function'
LINKED_POINTS = 'linked points'
LINKED_VALUED_POINTS = 'linked valued points'
LINKED_SEGMENTS = 'linked segments'
LINKED_VALUED_SEGMENTS = 'linked valued segments'
LINKED_GENOME_PARTITION = 'linked genome partition'
LINKED_STEP_FUNCTION = 'linked step function'
LINKED_FUNCTION = 'linked function'
LINKED_BASE_PAIRS = 'linked base pairs'

# Module methods

def _dtypeIsStringLongerThanOne(dtype):
    return any([ str(dtype).startswith(x) and int(str(dtype)[len(x):]) > 1 for x in ['S','|S'] ])

def inferValType(valList, shapeOffset=0):
    if valList is None:
        return False
    elif type(valList) in [list,tuple]:
        return 'number'
    elif isinstance(valList, numpy.ndarray) or isinstance(valList, SmartMemmap):
        if len(valList.shape) == 2 + shapeOffset and valList.shape[1 + shapeOffset] == 2 and valList.dtype == numpy.dtype('float128'):
            return 'mean_sd'
        elif any(valList.dtype == numpy.dtype(x) for x in ['float32', 'float64', 'float128']):
            if len( valList.shape ) == 1 + shapeOffset:
                return 'number'
            elif valList.shape[1 + shapeOffset] >= 2:
                return 'population'
        if any(valList.dtype == numpy.dtype(x) for x in ['int32', 'int64']):
            if len( valList.shape ) == 1 + shapeOffset:
                return 'number (integer)'
            elif valList.shape[1 + shapeOffset] >= 2:
                return 'population'
        elif any(valList.dtype == numpy.dtype(x) for x in ['int8', 'bool8']):
            if len( valList.shape ) == 1 + shapeOffset:
                return 'tc'
            elif valList.shape[1 + shapeOffset] >= 2:
                return 'tc_vector'
        elif valList.dtype == numpy.dtype('S1'):
            if len( valList.shape ) == 1 + shapeOffset:
                return 'char'
            elif valList.shape[1 + shapeOffset] >= 2:
                return 'char_vector'
        elif _dtypeIsStringLongerThanOne(valList.dtype):
            if len( valList.shape ) == 1 + shapeOffset:
                return 'category'
            elif valList.shape[1 + shapeOffset] >= 2:
                return 'category_vector'

        if valList.shape[1 + shapeOffset] == 0:
            return 'unsupported list'

        logMessage('Shape or dtype not recognized: ' + str(valList.shape) + ' and ' + str(valList.dtype) )
        raise ShouldNotOccurError()

    else:
        logMessage('Type of valList not recognized: ' + str(type(valList)))
        raise ShouldNotOccurError()

def inferWeightType(weightList):
    return inferValType(weightList, shapeOffset=1)

# Module classes

class TrackFormat(object):
    #dense, val, interval, linked
    FORMAT_DICT = {\
        POINTS: (False, False, False, False),\
        VALUED_POINTS: (False, True, False, False),\
        SEGMENTS: (False, False, True, False),\
        VALUED_SEGMENTS: (False, True, True, False),\
        GENOME_PARTITION: (True, False, True, False),\
        STEP_FUNCTION: (True, True, True, False),\
        FUNCTION: (True, True, False, False),\
        LINKED_POINTS: (False, False, False, True),\
        LINKED_VALUED_POINTS: (False, True, False, True),\
        LINKED_SEGMENTS: (False, False, True, True),\
        LINKED_VALUED_SEGMENTS: (False, True, True, True),\
        LINKED_GENOME_PARTITION: (True, False, True, True),\
        LINKED_STEP_FUNCTION: (True, True, True, True),\
        LINKED_FUNCTION: (True, True, False, True),\
        LINKED_BASE_PAIRS: (True, False, False, True)
        }

    VAL_TYPE_NAME_DICT = {
        'number': 'Number',\
        'number (integer)': 'Number (integer)',\
        'category' : 'Category',\
        'category_vector' : 'Vector of categories',\
        'tc' : 'Case-control',\
        'tc_vector' : 'Vector of case-control values',\
        'char' : 'Character',\
        'char_vector' : 'Vector of characters',\
        'mean_sd' : 'Mean and std.dev.',\
        'population' : 'Population vector'
    }

    @staticmethod
    def createInstanceFromGeSource(geSource):
        return TrackFormat.createInstanceFromPrefixList(geSource.getPrefixList(), \
                                                        geSource.getValDataType(), \
                                                        geSource.getValDim(), \
                                                        geSource.getEdgeWeightDataType(), \
                                                        geSource.getEdgeWeightDim())
    @staticmethod
    def createInstanceFromPrefixList(prefixList, valDataType='float64', valDim=1, weightDataType='float64', weightDim=1):
        if valDim is None:
            valDim = 3 #vector
        if weightDim is None:
            weightDim = 3 #vector

        lists = [ [] if prefix in prefixList else None for prefix in ['start', 'end'] ]

        if valDataType == 'S':
            valDataType = 'S2'
        if weightDataType == 'S':
            weightDataType = 'S2'

        if 'val' in prefixList:
            lists.append( numpy.array([], dtype=valDataType).reshape(0 if valDim == 1 else (0, valDim)) )
        else:
            lists.append(None)

        lists += [ [] if prefix in prefixList else None for prefix in ['strand','id','edges'] ]

        if 'weights' in prefixList:
            lists.append( numpy.array([], dtype=weightDataType).reshape((0, 0) if weightDim == 1 else (0, 0, weightDim)) )
        else:
            lists.append(None)

        lists.append(OrderedDict([(prefix,[]) for prefix in prefixList if prefix not in RESERVED_PREFIXES]) \
                     if any(prefix in RESERVED_PREFIXES for prefix in prefixList) else None)

        return TrackFormat( *lists )

    def __init__(self, startList=None, endList=None, valList=None, strandList=None, idList=None, edgesList=None, weightsList=None, extraLists=None):
        self._dense = (startList is None) #not trackData.has_key('start')
        self._val = inferValType(valList) #trackData.has_key('val')
        self._interval = (endList is not None) #trackData.has_key('end')
        self._linked = (edgesList is not None) #trackData.has_key('edges')
        self._reprDense = ((valList is not None or edgesList is not None) and startList is None and endList is None)
        #( trackData.has_key('val') or trackData.has_key('edges') ) and not trackData.has_key('start') and not trackData.has_key('end')
        self._hasStrand = (strandList is not None) #trackData.has_key('strand')
        self._hasId = (idList is not None) #trackData.has_key('strand')
        self._weights = inferWeightType(weightsList) #trackData.has_key('strand')
        self._extra = extraLists.keys() if extraLists is not None else False

    def isDense(self):
        return self._dense

    def isValued(self, specificValType=None):
        if specificValType is not None:
            return self._val == specificValType
        else:
            return self._val != False if self._val is not None else None

    def getValTypeName(self):
        if self.isValued():
            return self.VAL_TYPE_NAME_DICT[self._val]
        else:
            return ''

    def isInterval(self):
        return self._interval

    def isLinked(self):
        return self._linked

    def isPoints(self):
        return not self.isDense() and not self.isInterval()

    def isSegments(self):
        return not self.isDense() and self.isInterval()

    def isPartitionOrStepFunction(self):
        return self.isDense() and self.isInterval()

    def reprIsDense(self):
        return self._reprDense

    def hasStrand(self):
        return self._hasStrand

    def hasId(self):
        return self._hasId

    def isWeighted(self, specificWeightType=None):
        if specificWeightType is not None:
            return self._weights == specificWeightType
        else:
            return self._weights != False if self._weights is not None else None

    def getWeightTypeName(self):
        if self.isWeighted():
            return self.VAL_TYPE_NAME_DICT[self._weights]
        else:
            return ''

    def hasExtra(self, specificExtra=None):
        if specificExtra is not None:
            return self._extra not in [False, None] and specificExtra in self._extra
        else:
            return self._extra != False if self._extra is not None else None

    def getExtraNames(self):
        if self.hasExtra():
            return self._extra
        else:
            return []

    def getAllOverlapRules(self):
        # return [False] + ([True] if not self.isDense() else [])
        return [False, True]

    def getFormatName(self):
        for formatName, format in TrackFormat.FORMAT_DICT.iteritems():
            if (self._dense, (self._val != False), self._interval, self._linked) == format:
                return formatName.capitalize()
                #return formatName.capitalize() + ' (%s)'%self.getValTypeName() if self.isValued() else ''

        #print (self._dense, self._val, self._interval, self._linked)
        return 'Original elements'

    def __str__(self):
        return self.getFormatName()

    def __eq__(self, other):
        if not isinstance(other, TrackFormat):
            return False
        return self._dense == other._dense and \
               self._val == other._val and \
               self._interval == other._interval and \
               self._linked == other._linked and \
               self._reprDense == other._reprDense and \
               self._hasStrand == other._hasStrand and \
               self._hasId == other._hasId and \
               self._weights == other._weights and \
               self._extra == other._extra

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash( tuple( [self.__dict__[key] for key in sorted(self.__dict__.keys())] ) )

class TrackFormatReq(TrackFormat):
    '''
    Conversions between core informational properties and TrackFormatReq init parameters:

    Gaps -> not dense
    Lengths -> interval
    Values -> val
    Interconnections -> linked
    '''
    def __init__(self, dense=None, val=None, interval=None, linked=None, strand=None, id=None, weights=None, extra=None, \
                 allowOverlaps=False, borderHandling='crop', name=None):

        assert all(x in [None, False, True] for x in [dense, interval, linked, strand, id])
        assert all(x in [None, False] + TrackFormat.VAL_TYPE_NAME_DICT.keys() for x in [val, weights])
        assert extra in [None, False] or (type(extra) in [list, tuple] and len(extra) > 0 and
                                          isinstance(extra[0], basestring))
        assert allowOverlaps in [None, False, True]
        assert borderHandling in [None, 'crop','discard','include','duplicate']

        assert (name is None) or (dense is None and interval is None and linked is None)

        if name is not None:
            name = name.lower()
            if TrackFormatReq.FORMAT_DICT.has_key(name):
                self._dense, self._val, self._interval, self._linked = TrackFormatReq.FORMAT_DICT[name]

                if self._val:
                    assert val != False
                    self._val = val
                else:
                    assert val is None

                if not self._linked:
                    assert weights is None
                self._weights = weights
            else:
                raise NotSupportedError('Format name is not recognized: ' + name)
        else:
            self._dense = dense
            self._val = val
            self._interval = interval
            self._linked = linked
            self._weights = weights

        self._reprDense = None
        self._hasStrand = strand
        self._hasId = id
        self._extra = extra
        self._allowOverlaps = allowOverlaps
        self._borderHandling = borderHandling

    @classmethod
    def _getAttributes(cls, includeReqExtensions):
        return ['_dense','_val','_interval','_linked',\
                '_hasStrand','_hasId','_weights','_extra'] +\
               (['_allowOverlaps','_borderHandling'] if includeReqExtensions else [])

    def __str__(self):
        return 'Requirement: ' + ', '.join([ attr + ': ' + str(getattr(self, attr))\
                                             for attr in self._getAttributes(includeReqExtensions=True) \
                                             if getattr(self, attr) != None])

    def reprIsDense(self):
        raise NotSupportedError()

    def allowOverlaps(self):
        return self._allowOverlaps

    def borderHandling(self):
        return self._borderHandling

    # Compatibility with other TrackFormat, not TrackFormatReq. Does not need to handle allowsOverlap and borderHandling
    def isCompatibleWith(self, sourceFormat, exceptionList=[]):
        assert( not isinstance(sourceFormat, TrackFormatReq) )
        pairedAttrs = [ [getattr(obj, attr) for obj in [self,sourceFormat]] \
            for attr in self._getAttributes(includeReqExtensions=False) if attr[1:] not in exceptionList ]
        res = (not False in [s is None or s==sf for s,sf in pairedAttrs])
        return res

    @staticmethod
    def merge(mainReq, otherReq):
        "Tries to merge all not-None requirements of mainReq with other. Returns copy of mainReq if successful else returns None"
        outReq = copy.copy(mainReq)
        for attr in TrackFormatReq._getAttributes(includeReqExtensions=True):
            otherAttr = getattr(otherReq, attr)
            if otherAttr is not None:
                mainAttr = getattr(mainReq, attr)
                if mainAttr is None:
                    setattr(outReq, attr, otherAttr)
                elif mainAttr == otherAttr:
                    pass
                else:
                    return None
        return outReq

    @staticmethod
    def maxCommonCoreFormat(mainReq, otherReq):
        '''Finds the maximal common track format of mainReq and otherReq that
        maintains the "lengths" and "gaps" properties, but not "linked" and "valued".
        Returns copy of mainReq if successful else returns None'''
        outReq = copy.copy(mainReq)
        for attr in TrackFormatReq._getAttributes(includeReqExtensions=True):
            otherAttr = getattr(otherReq, attr)
            if otherAttr is not None:
                mainAttr = getattr(mainReq, attr)
                if mainAttr == otherAttr:
                    setattr(outReq, attr, otherAttr)
                elif attr in ['_val', '_linked']:
                    setattr(outReq, attr, False)
                else:
                    return None
        return outReq


class NeutralTrackFormatReq(TrackFormatReq):
    def __init__(self):
        TrackFormatReq.__init__(self, allowOverlaps=None, borderHandling=None)
