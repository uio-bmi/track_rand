from gold.formatconversion.FormatConverter import TrivialFormatConverter
from gold.formatconversion.SegmentToPointFormatConverter import SegmentToStartPointFormatConverter, \
    SegmentToMidPointFormatConverter, SegmentToEndPointFormatConverter
from gold.util.CommonFunctions import getClassName

ALL_CONVERTERS = [TrivialFormatConverter, SegmentToStartPointFormatConverter, SegmentToMidPointFormatConverter, \
                  SegmentToEndPointFormatConverter]

def getFormatConverters(sourceFormat, reqFormat):
    assert(reqFormat!=None)
    allObjects = [cls(sourceFormat, reqFormat) for cls in ALL_CONVERTERS]
    return [x for x in allObjects if x is not None]

def getFormatConverterByName(converterClassName):
    formatConverter = globals()[converterClassName]()
    assert( formatConverter.__class__ in ALL_CONVERTERS )
    return formatConverter
